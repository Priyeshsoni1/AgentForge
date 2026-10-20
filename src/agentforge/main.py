
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

from agentforge.api.agent_routes import router as agent_router
from agentforge.api.llm_routes import router as llm_router
from agentforge.core.agent import build_agent
from agentforge.core.config import settings
from agentforge.core.conversation_store import ConversationStore
from agentforge.core.security import (
    InMemoryRateLimiter,
    RedisRateLimiter,
)

logger = logging.getLogger(__name__)


class InMemoryConversationStore:
    """Development fallback; conversations are not durable."""

    def __init__(self):
        self.owners = {}

    async def claim_or_verify(self, thread_id: str, owner_id: str) -> None:
        existing = self.owners.get(thread_id)

        if existing is not None and existing != owner_id:
            raise PermissionError("Conversation ownership mismatch.")

        self.owners[thread_id] = owner_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    environment = settings.environment.lower()

    if environment != "development":
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required in production.")

        if not settings.redis_url:
            raise RuntimeError("REDIS_URL is required in production.")

        if not settings.app_api_keys:
            raise RuntimeError("APP_API_KEYS is required in production.")

    app.state.agent_graph = None
    app.state.redis = None
    app.state.db_pool = None

    database_url = (
        settings.database_url.get_secret_value()
        if settings.database_url
        else None
    )

    if database_url:
        pool = AsyncConnectionPool(
            conninfo=database_url,
            min_size=1,
            max_size=5,
            open=False,
        )
        await pool.open()
        app.state.db_pool = pool

        try:
            await pool.wait()

            store = ConversationStore(pool)
            await store.setup()
            app.state.conversation_store = store

            async with AsyncPostgresSaver.from_conn_string(
                database_url
            ) as checkpointer:
                await checkpointer.setup()

                if settings.openrouter_api_key:
                    app.state.agent_graph = build_agent(
                        checkpointer=checkpointer
                    )

                await initialize_rate_limiter(app)
                yield
        finally:
            if app.state.redis is not None:
                await app.state.redis.aclose()

            await pool.close()
    else:
        if environment != "development":
            raise RuntimeError("Database configuration is required.")

        app.state.conversation_store = InMemoryConversationStore()

        if settings.openrouter_api_key:
            app.state.agent_graph = build_agent()

        await initialize_rate_limiter(app)

        try:
            yield
        finally:
            if app.state.redis is not None:
                await app.state.redis.aclose()


async def initialize_rate_limiter(app: FastAPI) -> None:
    if settings.redis_url:
        redis_client = Redis.from_url(
            settings.redis_url.get_secret_value(),
            decode_responses=True,
        )
        await redis_client.ping()

        app.state.redis = redis_client
        app.state.rate_limiter = RedisRateLimiter(
            redis_client,
            settings.rate_limit_requests,
            settings.rate_limit_window_seconds,
        )
    elif settings.environment.lower() == "development":
        app.state.rate_limiter = InMemoryRateLimiter(
            settings.rate_limit_requests,
            settings.rate_limit_window_seconds,
        )
    else:
        raise RuntimeError("Redis is required outside development.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-oriented multi-tool AI agent.",
    lifespan=lifespan,
)

app.include_router(llm_router)
app.include_router(agent_router)


@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    return {
        "project": settings.app_name,
        "message": "Welcome to AgentForge",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "agentforge-api",
        "version": settings.app_version,
    }
