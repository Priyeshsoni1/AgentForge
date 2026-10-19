
from fastapi import APIRouter, HTTPException
from langgraph.errors import GraphRecursionError

from agentforge.api.schemas import AgentRunRequest, AgentRunResponse
from agentforge.core.agent import run_agent

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
            detail="Agent reached its execution limit. Try a simpler task.",
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
        # Keep unexpected internal details out of the HTTP response.
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed.",
        ) from exc
