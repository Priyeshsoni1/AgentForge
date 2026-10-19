
import pytest
from fastapi.testclient import TestClient

from agentforge.api import agent_routes
from agentforge.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_agent_run_returns_answer(client, monkeypatch):
    async def fake_run_agent(message: str) -> dict:
        return {
            "answer": "The result is 100.",
            "tool_calls": [
                {
                    "name": "calculator",
                    "arguments": {"expression": "25 * 4"},
                }
            ],
            "steps": 3,
        }

    monkeypatch.setattr(agent_routes, "run_agent", fake_run_agent)

    response = client.post(
        "/agent/run",
        json={"message": "Calculate 25 times 4."},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "The result is 100."
    assert response.json()["tool_calls"][0]["name"] == "calculator"


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
    async def fake_run_agent(message: str) -> dict:
        raise RuntimeError("Agent unavailable.")

    monkeypatch.setattr(agent_routes, "run_agent", fake_run_agent)

    response = client.post(
        "/agent/run",
        json={"message": "Hello"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Agent unavailable."
