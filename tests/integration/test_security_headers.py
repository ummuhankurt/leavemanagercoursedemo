"""Security headers on API, static and error responses (spec 0002, AC-11)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_api_and_static_responses_carry_security_headers(client: TestClient) -> None:
    responses = {
        "api": client.get("/api/v1/health"),
        "page": client.get("/"),
        "script": client.get("/app.js"),
        "unauthorized": client.get("/api/v1/auth/me"),
        "not found": client.get("/api/v1/does-not-exist"),
    }

    for name, response in responses.items():
        assert response.headers.get("content-security-policy") == "default-src 'self'", name
        assert response.headers.get("x-content-type-options") == "nosniff", name
        assert response.headers.get("referrer-policy") == "no-referrer", name
