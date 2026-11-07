"""Framework errors in the standard body (spec 0002, AC-8; closes backlog B-1)."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

LOGIN = "/api/v1/auth/login"
VALIDATION_BODY = {"error": {"code": "VALIDATION_ERROR", "message": "Geçersiz istek."}}


@pytest.mark.parametrize(
    "payload",
    [
        {"password": "gizli-sifre-123"},
        {"email": "ayse@example.com"},
        {"email": "   ", "password": "gizli-sifre-123"},
        {"email": "ayse@example.com", "password": ""},
        {"email": "ayse@example.com", "password": "gizli-sifre-123", "role": "HR"},
        {"email": 42, "password": "gizli-sifre-123"},
    ],
)
def test_invalid_login_body_returns_422_standard_body(
    client: TestClient, payload: dict[str, Any]
) -> None:
    response = client.post(LOGIN, json=payload)

    assert response.status_code == 422
    assert response.json() == VALIDATION_BODY
    assert "gizli-sifre-123" not in response.text


def test_malformed_json_returns_422_standard_body(client: TestClient) -> None:
    response = client.post(
        LOGIN, content=b"{not json", headers={"content-type": "application/json"}
    )

    assert response.status_code == 422
    assert response.json() == VALIDATION_BODY


@pytest.mark.parametrize("path", ["/api/v1/does-not-exist", "/no-such-page.html"])
def test_unknown_path_returns_404_standard_body(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "NOT_FOUND", "message": "Kaynak bulunamadı."}}


def test_wrong_method_returns_405_standard_body(client: TestClient) -> None:
    response = client.get(LOGIN)

    assert response.status_code == 405
    assert response.json() == {
        "error": {"code": "METHOD_NOT_ALLOWED", "message": "Bu yöntem desteklenmiyor."}
    }
    assert "POST" in response.headers["allow"]
