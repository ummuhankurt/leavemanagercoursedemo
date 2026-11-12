"""Session service rules, without a database (spec 0002, AC-2…AC-5)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from leave_manager.core.clock import FixedClock
from leave_manager.core.errors import ForbiddenError, UnauthorizedError
from leave_manager.core.passwords import hash_password
from leave_manager.models import User, UserRole
from leave_manager.services.auth import (
    SESSION_DURATION,
    check_csrf,
    ensure_demo_users,
    resolve_session,
    start_session,
)

SECRET = "unit-test-secret"
PASSWORD = "dogru-sifre"
LOGIN_AT = datetime(2026, 11, 7, 9, 0, tzinfo=UTC)


class FakeUsers:
    def __init__(self) -> None:
        self._by_id: dict[int, User] = {}

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._by_id.values() if u.email == email), None)

    def get_by_id(self, user_id: int) -> User | None:
        return self._by_id.get(user_id)

    def all(self) -> list[User]:
        return list(self._by_id.values())

    def add(self, user: User) -> User:
        user.id = len(self._by_id) + 1
        self._by_id[user.id] = user
        return user


@pytest.fixture
def users() -> FakeUsers:
    store = FakeUsers()
    store.add(
        User(
            email="ayse@example.com",
            name="Ayşe",
            role=UserRole.EMPLOYEE,
            password_hash=hash_password(PASSWORD),
        )
    )
    return store


def _login(users: FakeUsers, email: str = "ayse@example.com", password: str = PASSWORD) -> str:
    return start_session(users, email, password, FixedClock(LOGIN_AT), SECRET).token


def test_login_normalizes_email_case_and_whitespace(users: FakeUsers) -> None:
    result = start_session(users, "  AySe@Example.COM \t", PASSWORD, FixedClock(LOGIN_AT), SECRET)

    assert result.user.email == "ayse@example.com"
    assert result.user.role is UserRole.EMPLOYEE


def test_password_is_compared_exactly(users: FakeUsers) -> None:
    with pytest.raises(UnauthorizedError):
        _login(users, password=PASSWORD.upper())
    with pytest.raises(UnauthorizedError):
        _login(users, password=f" {PASSWORD}")


def test_unknown_email_and_wrong_password_raise_same_error(users: FakeUsers) -> None:
    with pytest.raises(UnauthorizedError) as wrong_password:
        _login(users, password="yanlis")
    with pytest.raises(UnauthorizedError) as unknown_email:
        _login(users, email="kimse@example.com")

    assert (wrong_password.value.code, wrong_password.value.message) == (
        unknown_email.value.code,
        unknown_email.value.message,
    )


def test_session_valid_one_second_before_eight_hours(users: FakeUsers) -> None:
    token = _login(users)
    almost = FixedClock(LOGIN_AT + SESSION_DURATION - timedelta(seconds=1))

    assert resolve_session(users, token, almost, SECRET).email == "ayse@example.com"


def test_session_expired_at_exactly_eight_hours(users: FakeUsers) -> None:
    token = _login(users)

    for moment in (LOGIN_AT + SESSION_DURATION, LOGIN_AT + SESSION_DURATION + timedelta(days=1)):
        with pytest.raises(UnauthorizedError):
            resolve_session(users, token, FixedClock(moment), SECRET)


def test_session_rejected_when_missing_tampered_from_future_or_user_gone(
    users: FakeUsers,
) -> None:
    token = _login(users)
    now = FixedClock(LOGIN_AT + timedelta(minutes=5))

    for raw in (None, "", token[:-2] + "xx"):
        with pytest.raises(UnauthorizedError):
            resolve_session(users, raw, now, SECRET)
    with pytest.raises(UnauthorizedError):
        resolve_session(users, token, FixedClock(LOGIN_AT - timedelta(seconds=1)), SECRET)
    with pytest.raises(UnauthorizedError):
        resolve_session(FakeUsers(), token, now, SECRET)


def test_csrf_must_match_the_session_token(users: FakeUsers) -> None:
    session = resolve_session(users, _login(users), FixedClock(LOGIN_AT), SECRET)

    check_csrf(session, session.csrf_token)
    for presented in (None, "", "wrong", session.csrf_token + "x"):
        with pytest.raises(ForbiddenError):
            check_csrf(session, presented)


def test_each_login_gets_its_own_csrf_token(users: FakeUsers) -> None:
    first = start_session(users, "ayse@example.com", PASSWORD, FixedClock(LOGIN_AT), SECRET)
    second = start_session(users, "ayse@example.com", PASSWORD, FixedClock(LOGIN_AT), SECRET)

    assert first.user.csrf_token != second.user.csrf_token


def test_demo_users_cover_every_role_and_are_not_duplicated() -> None:
    store = FakeUsers()

    assert ensure_demo_users(store, "demo-pass") == len(UserRole)
    assert ensure_demo_users(store, "demo-pass") == 0
    assert {user.role for user in store.all()} == set(UserRole)
