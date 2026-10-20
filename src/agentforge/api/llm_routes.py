
from fastapi import APIRouter, Depends, HTTPException,Depends

from agentforge.api.schemas import ChatRequest, ChatResponse
from agentforge.core.llm import (
    LLMConfigurationError,
    LLMProviderError,
    OpenRouterClient,
)
from agentforge.core.security import enforce_rate_limit, get_current_owner
router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
    dependencies=[
       
        Depends(enforce_rate_limit),
    ],
)


def get_openrouter_client() -> OpenRouterClient:
    return OpenRouterClient()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    client: OpenRouterClient = Depends(get_openrouter_client),
) -> ChatResponse:
    try:
        result = await client.chat(request.message)
        return ChatResponse(**result)

    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="LLM provider is not configured.",
        ) from exc

    except LLMProviderError as exc:
        status_code = (
            503 if "rate limit" in str(exc).lower() else 502
        )
        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc
