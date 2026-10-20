
import json

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from agentforge.api import agent_routes
from agentforge.core.config import settings
from agentforge.core.security import (
    InMemoryRateLimiter,
    get_api_key_owners,
)
from agentforge.main import app


def test_api_key_configuration_parses_owner_mapping(monkeypatch):
    monkeypatch.setattr(
        settings,
        "app_api_keys",
        SecretStr(json.dumps({"alice": "a" * 32})),
    )

    assert get_api_key_owners() == {"alice": "a" * 32}


def test_invalid_api_key_is_rejected(monkeypatch):
    monkeypatch.setattr(
        settings,
        "app_api_keys",
        SecretStr(json.dumps({"alice": "a" * 32})),
    )
    monkeypatch.setattr(settings, "database_url", None)
    monkeypatch.setattr(settings, "openrouter_api_key", None)

    with TestClient(app) as client:
        response = client.post(
            "/agent/run",
            headers={"X-API-Key": "wrong-key"},
            json={"message": "Hello"},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_in_memory_rate_limiter():
    limiter = InMemoryRateLimiter(limit=2, window_seconds=60)

    assert await limiter.check("alice") is True
    assert await limiter.check("alice") is True
    assert await limiter.check("alice") is False
    assert await limiter.check("bob") is True


def test_conversation_owner_mismatch_returns_not_found(
    monkeypatch,
):
    monkeypatch.setattr(settings, "database_url", None)
    monkeypatch.setattr(settings, "openrouter_api_key", None)
    monkeypatch.setattr(
        settings,
        "app_api_keys",
        SecretStr(json.dumps({
            "alice": "a" * 32,
            "bob": "b" * 32,
        })),
    )

    async def fake_run_agent(message, graph=None, thread_id=None):
        return {
            "answer": "Hello",
            "tool_calls": [],
            "steps": 1,
            "thread_id": thread_id,
        }

    monkeypatch.setattr(agent_routes, "run_agent", fake_run_agent)

    with TestClient(app) as client:
        first = client.post(
            "/agent/run",
            headers={"X-API-Key": "a" * 32},
            json={
                "message": "Hello",
                "thread_id": "alice-private-thread",
            },
        )

        second = client.post(
            "/agent/run",
            headers={"X-API-Key": "b" * 32},
            json={
                "message": "Read my previous conversation.",
                "thread_id": "alice-private-thread",
            },
        )

    assert first.status_code == 200
    assert second.status_code == 404
