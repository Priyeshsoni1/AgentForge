
from fastapi import FastAPI

from agentforge.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-oriented multi-tool AI agent.",
)


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
