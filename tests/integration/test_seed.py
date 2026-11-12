"""Seed command (spec 0002, AC-7)."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select

from leave_manager.core.config import DATABASE_URL_ENV
from leave_manager.core.db import Database
from leave_manager.core.passwords import verify_password
from leave_manager.models import User, UserRole
from leave_manager.seed import DEMO_PASSWORD_ENV, run

DEMO_PASSWORD = "seed-test-password"


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "seed.db"


def _env(db_path: Path, password: str | None = DEMO_PASSWORD) -> dict[str, str]:
    env = {DATABASE_URL_ENV: f"sqlite:///{db_path.as_posix()}"}
    if password is not None:
        env[DEMO_PASSWORD_ENV] = password
    return env


def _users(db_path: Path) -> list[User]:
    database = Database(f"sqlite:///{db_path.as_posix()}")
    try:
        with database.session() as session:
            users = list(session.scalars(select(User)))
            session.expunge_all()
            return users
    finally:
        database.dispose()


def test_seed_creates_one_user_per_role_with_argon2_hash(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(_env(db_path)) == 0

    users = _users(db_path)
    assert sorted(user.role for user in users) == sorted(UserRole)
    for user in users:
        assert user.password_hash.startswith("$argon2id$")
        assert DEMO_PASSWORD not in user.password_hash
        assert verify_password(user.password_hash, DEMO_PASSWORD)
    output = capsys.readouterr()
    assert DEMO_PASSWORD not in output.out + output.err


def test_seed_is_idempotent(db_path: Path) -> None:
    run(_env(db_path))
    first = {(user.id, user.email, user.password_hash) for user in _users(db_path)}

    assert run(_env(db_path, password="another-password")) == 0

    assert {(user.id, user.email, user.password_hash) for user in _users(db_path)} == first


@pytest.mark.parametrize("password", [None, "", "   "])
def test_seed_without_demo_password_creates_nothing(
    db_path: Path, capsys: pytest.CaptureFixture[str], password: str | None
) -> None:
    assert run(_env(db_path, password=password)) == 1

    assert not db_path.exists()
    assert DEMO_PASSWORD_ENV in capsys.readouterr().err
