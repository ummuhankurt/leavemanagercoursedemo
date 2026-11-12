"""Spec 0001 AC-1, AC-2 — status query over HTTP against a real SQLite database."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

from fastapi.testclient import TestClient


def test_health_reports_ok_version_and_database(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": metadata.version("leave-manager"),
        "database": "reachable",
    }


def test_health_returns_503_standard_error_without_internals(
    unreachable_client: TestClient, unreachable_db_path: Path
) -> None:
    response = unreachable_client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {
        "error": {"code": "SERVICE_UNAVAILABLE", "message": "Hizmet şu anda kullanılamıyor."}
    }
    body = response.text.lower()
    for internal in ("select", "sqlite", "traceback", unreachable_db_path.name, "missing-dir"):
        assert internal not in body
