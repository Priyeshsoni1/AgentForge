
from fastapi import FastAPI
from fastapi.testclient import TestClient

from agentforge.core.observability import RequestLoggingMiddleware


def test_request_id_is_returned():
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get("/test")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_valid_request_id_is_preserved():
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get(
            "/test",
            headers={"X-Request-ID": "ci-test-123"},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "ci-test-123"


def test_invalid_request_id_is_replaced():
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get(
            "/test",
            headers={"X-Request-ID": "invalid id with spaces"},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "invalid id with spaces"
