
import asyncio
import json
import logging
from collections.abc import AsyncIterator
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from langgraph.errors import GraphRecursionError

from agentforge.api.schemas import AgentRunRequest, AgentRunResponse
from agentforge.core.agent import run_agent, stream_agent
from agentforge.core.security import (
    enforce_rate_limit,
    get_current_owner,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
    dependencies=[Depends(enforce_rate_limit)],
)


async def verify_conversation(
    request: Request,
    thread_id: str,
    owner_id: str,
) -> None:
    try:
        await request.app.state.conversation_store.claim_or_verify(
            thread_id,
            owner_id,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        ) from exc


@router.post("/run", response_model=AgentRunResponse)
async def run_agent_endpoint(
    request: AgentRunRequest,
    http_request: Request,
    owner_id: str = Depends(get_current_owner),
) -> AgentRunResponse:
    thread_id = request.thread_id or str(uuid4())

    await verify_conversation(http_request, thread_id, owner_id)

    try:
        result = await run_agent(
            request.message,
            graph=http_request.app.state.agent_graph,
            thread_id=thread_id,
        )
        result["thread_id"] = thread_id
        return AgentRunResponse(**result)

    except GraphRecursionError as exc:
        raise HTTPException(
            status_code=422,
            detail="Agent execution limit reached.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except RuntimeError as exc:
        logger.warning("Agent execution unavailable: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Agent execution unavailable.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected agent execution failure")
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed.",
        ) from exc


def encode_sse(event: str, data: dict) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )


async def agent_event_stream(
    message: str,
    graph,
    thread_id: str,
) -> AsyncIterator[str]:
    try:
        async for item in stream_agent(
            message,
            graph=graph,
            thread_id=thread_id,
        ):
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
    http_request: Request,
    owner_id: str = Depends(get_current_owner),
) -> StreamingResponse:
    thread_id = request.thread_id or str(uuid4())

    await verify_conversation(http_request, thread_id, owner_id)

    return StreamingResponse(
        agent_event_stream(
            request.message,
            http_request.app.state.agent_graph,
            thread_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
