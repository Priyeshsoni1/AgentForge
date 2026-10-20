
import pytest
from fastapi.testclient import TestClient

from agentforge.api import agent_routes
from agentforge.core.config import settings
from agentforge.main import app


@pytest.fixture
def client(monkeypatch):
    # Keep API unit tests independent of a real database.
    monkeypatch.setattr(settings, "database_url", None)
    monkeypatch.setattr(settings, "openrouter_api_key", None)

    with TestClient(app) as test_client:
        yield test_client


def test_agent_run_returns_answer(client, monkeypatch):
    async def fake_run_agent(
        message: str,
        graph=None,
        thread_id=None,
    ) -> dict:
        return {
            "answer": "The result is 100.",
            "tool_calls": [
                {
                    "name": "calculator",
                    "arguments": {"expression": "25 * 4"},
                }
            ],
            "steps": 3,
            "thread_id": thread_id,
        }

    monkeypatch.setattr(agent_routes, "run_agent", fake_run_agent)

    response = client.post(
        "/agent/run",
        json={
            "message": "Calculate 25 times 4.",
            "thread_id": "test-conversation",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "The result is 100."
    assert response.json()["thread_id"] == "test-conversation"


def test_agent_rejects_empty_message(client):
    response = client.post(
        "/agent/run",
        json={"message": "   "},
    )

    assert response.status_code == 422


def test_agent_rejects_oversized_message(client):
    response = client.post(
        "/agent/run",
        json={"message": "a" * 4001},
    )

    assert response.status_code == 422


def test_agent_handles_execution_failure(client, monkeypatch):
    async def fake_run_agent(message, graph=None, thread_id=None):
        raise RuntimeError("Agent unavailable.")

    monkeypatch.setattr(agent_routes, "run_agent", fake_run_agent)

    response = client.post(
        "/agent/run",
        json={"message": "Hello"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Agent execution unavailable."
