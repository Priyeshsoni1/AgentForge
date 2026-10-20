
import asyncio
import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langgraph.errors import GraphRecursionError

from agentforge.api.schemas import AgentRunRequest, AgentRunResponse
from agentforge.core.agent import run_agent, stream_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/run", response_model=AgentRunResponse)
async def run_agent_endpoint(
    request: AgentRunRequest,
) -> AgentRunResponse:
    try:
        result = await run_agent(request.message)
        return AgentRunResponse(**result)

    except GraphRecursionError as exc:
        raise HTTPException(
            status_code=422,
            detail="Agent reached its execution limit.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


    except Exception as exc:
        logger.exception("Unexpected agent execution failure")
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed.",
        ) from exc


def encode_sse(event: str, data: dict) -> str:
    """Serialize one Server-Sent Event."""
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )



async def agent_event_stream(
    message: str,
) -> AsyncIterator[str]:
    try:
        async for item in stream_agent(message):
            yield encode_sse(item["event"], item["data"])

    except asyncio.CancelledError:
        raise

    except GraphRecursionError:
        yield encode_sse(
            "error",
            {"message": "Agent execution limit reached."},
        )

    except Exception:
        logger.exception("Agent streaming failed")
        yield encode_sse(
            "error",
            {"message": "Agent execution failed."},
        )

    yield encode_sse("done", {"completed": True})


@router.post("/run/stream")
async def run_agent_stream_endpoint(
    request: AgentRunRequest,
) -> StreamingResponse:
    return StreamingResponse(
        agent_event_stream(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
