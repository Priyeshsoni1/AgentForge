
import pytest
from fastapi.testclient import TestClient

from agentforge.api.llm_routes import get_openrouter_client
from agentforge.core.llm import LLMProviderError
from agentforge.main import app


class FakeOpenRouterClient:
    async def chat(self, message: str) -> dict:
        return {
            "answer": f"Test response for: {message}",
            "model": "test-model",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 8,
                "total_tokens": 18,
            },
        }


class FailingOpenRouterClient:
    async def chat(self, message: str) -> dict:
        raise LLMProviderError("Test provider failure.")


@pytest.fixture
def client():
    app.dependency_overrides[get_openrouter_client] = (
        lambda: FakeOpenRouterClient()
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_success(client):
    response = client.post(
        "/llm/chat",
        json={"message": "Explain Python briefly."},
    )

    assert response.status_code == 200
    assert response.json()["model"] == "test-model"
    assert "Explain Python briefly." in response.json()["answer"]
    assert response.json()["usage"]["total_tokens"] == 18


def test_chat_rejects_empty_message(client):
    response = client.post(
        "/llm/chat",
        json={"message": "   "},
    )

    assert response.status_code == 422


def test_chat_rejects_long_message(client):
    response = client.post(
        "/llm/chat",
        json={"message": "a" * 4001},
    )

    assert response.status_code == 422


def test_provider_failure_returns_gateway_error():
    app.dependency_overrides[get_openrouter_client] = (
        lambda: FailingOpenRouterClient()
    )

    try:
        with TestClient(app) as test_client:
            response = test_client.post(
                "/llm/chat",
                json={"message": "Hello"},
            )

        assert response.status_code == 502
        assert response.json()["detail"] == "Test provider failure."
    finally:
        app.dependency_overrides.clear()
