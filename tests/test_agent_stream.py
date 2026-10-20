
import json

from fastapi.testclient import TestClient

from agentforge.api import agent_routes
from agentforge.main import app


def test_stream_returns_sse_content_type(monkeypatch):
    async def fake_stream(message: str):
        yield {
            "event": "status",
            "data": {"message": "Agent execution started."},
        }
        yield {
            "event": "final",
            "data": {"answer": "Hello from AgentForge."},
        }

    monkeypatch.setattr(agent_routes, "stream_agent", fake_stream)

    with TestClient(app) as client:
        response = client.post(
            "/agent/run/stream",
            json={"message": "Say hello"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/event-stream"
    )
    assert "event: status" in response.text
    assert "event: final" in response.text
    assert "Hello from AgentForge." in response.text
    assert "event: done" in response.text


def test_stream_rejects_empty_message():
    with TestClient(app) as client:
        response = client.post(
            "/agent/run/stream",
            json={"message": "   "},
        )

    assert response.status_code == 422


def test_sse_encoding():
    encoded = agent_routes.encode_sse(
        "final",
        {"answer": "Hello"},
    )

    assert encoded.startswith("event: final\n")
    assert json.loads(encoded.split("data: ", 1)[1]) == {
        "answer": "Hello"
    }
