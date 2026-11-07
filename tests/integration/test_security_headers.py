"""Security headers on API, static and error responses (spec 0002, AC-11)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from httpx import Response

from leave_manager.core.config import Settings
from leave_manager.main import create_app


def _assert_security_headers(response: Response, name: str) -> None:
    assert response.headers.get("content-security-policy") == "default-src 'self'", name
    assert response.headers.get("x-content-type-options") == "nosniff", name
    assert response.headers.get("referrer-policy") == "no-referrer", name


def test_api_and_static_responses_carry_security_headers(client: TestClient) -> None:
    responses = {
        "api": client.get("/api/v1/health"),
        "page": client.get("/"),
        "script": client.get("/app.js"),
        "unauthorized": client.get("/api/v1/auth/me"),
        "not found": client.get("/api/v1/does-not-exist"),
    }

    for name, response in responses.items():
        _assert_security_headers(response, name)


def test_unexpected_error_response_carries_security_headers(database_url: str) -> None:
    app = create_app(Settings(database_url=database_url, session_secret="test-secret"))

    def boom() -> None:
        raise RuntimeError("internal detail that must not leak")

    app.add_api_route("/api/v1/test-boom", boom)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/v1/test-boom")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "internal detail" not in response.text
    _assert_security_headers(response, "500")
