"""Shared fixtures and the fast/full selector (docs/testing.md, Two speeds, rule 4)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from leave_manager.core.config import Settings
from leave_manager.main import create_app

INTEGRATION_DIR = Path(__file__).parent / "integration"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # Every test under tests/integration/ is full-only; everything else runs in --fast.
    for item in items:
        if INTEGRATION_DIR in Path(item.path).parents:
            item.add_marker(pytest.mark.integration)


def _client_for(database_url: str) -> Iterator[TestClient]:
    # Context manager: runs the app lifespan, so the engine is disposed at the end of the test.
    with TestClient(create_app(Settings(database_url=database_url))) as client:
        yield client


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    """App on a fresh SQLite file of its own — nothing reaches the next test or run."""
    yield from _client_for(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")


@pytest.fixture
def unreachable_db_path(tmp_path: Path) -> Path:
    """A database file inside a directory that does not exist: connecting really fails."""
    return tmp_path / "missing-dir" / "test.db"


@pytest.fixture
def unreachable_client(unreachable_db_path: Path) -> Iterator[TestClient]:
    yield from _client_for(f"sqlite:///{unreachable_db_path.as_posix()}")
