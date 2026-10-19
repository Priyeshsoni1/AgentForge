
import httpx

from agentforge.core.config import settings


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMServiceError(Exception):
    """Base exception for LLM service failures."""


class LLMConfigurationError(LLMServiceError):
    """Raised when the LLM provider is not configured."""


class LLMProviderError(LLMServiceError):
    """Raised when the upstream provider fails."""


class OpenRouterClient:
    async def chat(self, message: str) -> dict:
        if not settings.openrouter_api_key:
            raise LLMConfigurationError(
                "OpenRouter API key is not configured."
            )

        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are AgentForge, a helpful AI assistant. "
                        "Answer clearly and honestly."
                    ),
                },
                {"role": "user", "content": message},
            ],
            "max_tokens": settings.openrouter_max_tokens,
            "temperature": 0.2,
        }

        headers = {
            "Authorization": (
                f"Bearer {settings.openrouter_api_key.get_secret_value()}"
            ),
            "Content-Type": "application/json",
        }

        timeout = httpx.Timeout(settings.openrouter_timeout_seconds)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                )

            if response.status_code == 429:
                raise LLMProviderError(
                    "OpenRouter rate limit reached. Try again later."
                )

            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise LLMProviderError(
                    "The model returned an empty response."
                )

            usage = data.get("usage") or {}

            return {
                "answer": content.strip(),
                "model": data.get("model", settings.openrouter_model),
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                },
            }

        except LLMProviderError:
            raise
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                "OpenRouter request timed out."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"OpenRouter returned HTTP {exc.response.status_code}."
            ) from exc
        except (httpx.RequestError, ValueError, KeyError, IndexError) as exc:
            raise LLMProviderError(
                "Could not obtain a valid response from OpenRouter."
            ) from exc
