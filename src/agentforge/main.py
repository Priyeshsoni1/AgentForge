
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agentforge.api.agent_routes import router as agent_router
from agentforge.api.llm_routes import router as llm_router
from agentforge.core.agent import build_agent
from agentforge.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent_graph = None

    if settings.database_url:
        async with AsyncPostgresSaver.from_conn_string(
            settings.database_url.get_secret_value()
        ) as checkpointer:
            await checkpointer.setup()

            if settings.openrouter_api_key:
                app.state.agent_graph = build_agent(
                    checkpointer=checkpointer
                )

            yield
    else:
        logger.warning(
            "DATABASE_URL is not configured; checkpoint persistence is disabled."
        )

        if settings.openrouter_api_key:
            app.state.agent_graph = build_agent()

        yield


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
