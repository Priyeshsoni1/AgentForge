
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=4000)


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class ChatResponse(BaseModel):
    answer: str
    model: str
    usage: TokenUsage


class AgentRunRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=4000)
    thread_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Reuse this ID to continue a conversation.",
    )


class ToolCallInfo(BaseModel):
    name: str
    arguments: dict


class AgentRunResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCallInfo]
    steps: int
    thread_id: str
