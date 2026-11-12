"""Shared fixtures and the fast/full selector (docs/testing.md, Two speeds, rule 4)."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from leave_manager.core.config import Settings
from leave_manager.core.db import Database, migrate
from leave_manager.core.passwords import hash_password
from leave_manager.main import create_app
from leave_manager.models import User, UserRole
from leave_manager.repositories.users import UserRepository

INTEGRATION_DIR = Path(__file__).parent / "integration"
# Test-only signing key: tests never depend on a real secret (spec 0002, Constraints).
TEST_SESSION_SECRET = "test-session-secret-not-for-production"

CreateUser = Callable[..., User]


def make_settings(database_url: str, *, cookie_secure: bool = False) -> Settings:
    return Settings(
        database_url=database_url,
        session_secret=TEST_SESSION_SECRET,
        cookie_secure=cookie_secure,
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # Every test under tests/integration/ is full-only; everything else runs in --fast.
    for item in items:
        if INTEGRATION_DIR in Path(item.path).parents:
            item.add_marker(pytest.mark.integration)


def client_for(settings: Settings) -> Iterator[TestClient]:
    # Context manager: runs the app lifespan, so the engine is disposed at the end of the test.
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    """A fresh SQLite file with all migrations applied (docs/testing.md, Integration)."""
    url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    migrate(url)
    return url


@pytest.fixture
def client(database_url: str) -> Iterator[TestClient]:
    """App on a fresh SQLite file of its own — nothing reaches the next test or run."""
    yield from client_for(make_settings(database_url))


@pytest.fixture
def secure_client(database_url: str) -> Iterator[TestClient]:
    """Same app with the production cookie setting (Secure)."""
    yield from client_for(make_settings(database_url, cookie_secure=True))


@pytest.fixture
def create_user(database_url: str) -> Iterator[CreateUser]:
    """Insert a user with a known password into the test database."""
    database = Database(database_url)

    def create(
        email: str = "ayse@example.com",
        password: str = "dogru-sifre",
        name: str = "Ayşe Yılmaz",
        role: UserRole = UserRole.EMPLOYEE,
    ) -> User:
        with database.session() as session:
            user = User(email=email, name=name, role=role, password_hash=hash_password(password))
            UserRepository(session).add(user)
            session.expunge(user)
            return user

    yield create
    database.dispose()


@pytest.fixture
def unreachable_db_path(tmp_path: Path) -> Path:
    """A database file inside a directory that does not exist: connecting really fails."""
    return tmp_path / "missing-dir" / "test.db"


@pytest.fixture
def unreachable_client(unreachable_db_path: Path) -> Iterator[TestClient]:
    yield from client_for(make_settings(f"sqlite:///{unreachable_db_path.as_posix()}"))
