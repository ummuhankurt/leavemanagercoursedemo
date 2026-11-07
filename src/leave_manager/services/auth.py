"""Sessions: log in, resolve the current user, CSRF check, demo users (spec 0002).

Sensitive area: Yetkilendirme (docs/domain.md). Every later authorization decision starts from
the SessionUser returned here.
"""

from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from leave_manager.core.clock import Clock
from leave_manager.core.db import Database
from leave_manager.core.errors import ForbiddenError, UnauthorizedError
from leave_manager.core.passwords import dummy_hash, hash_password, verify_password
from leave_manager.core.tokens import SessionToken, sign, verify
from leave_manager.models import User, UserRole
from leave_manager.repositories.users import UserRepository

# Fixed lifetime from the moment of login; use does not extend it (spec 0002, R-5).
SESSION_DURATION = timedelta(hours=8)

INVALID_CREDENTIALS_CODE = "INVALID_CREDENTIALS"
INVALID_CREDENTIALS_MESSAGE = "E-posta veya şifre hatalı."
NOT_LOGGED_IN_CODE = "NOT_LOGGED_IN"
NOT_LOGGED_IN_MESSAGE = "Oturum açılmamış."
CSRF_INVALID_CODE = "CSRF_TOKEN_INVALID"
CSRF_INVALID_MESSAGE = "İstek doğrulanamadı."


class UserStore(Protocol):
    def get_by_email(self, email: str) -> User | None: ...
    def get_by_id(self, user_id: int) -> User | None: ...
    def add(self, user: User) -> User: ...


@dataclass(frozen=True)
class SessionUser:
    id: int
    name: str
    email: str
    role: UserRole
    csrf_token: str


@dataclass(frozen=True)
class LoginResult:
    token: str
    user: SessionUser


@dataclass(frozen=True)
class DemoUser:
    email: str
    name: str
    role: UserRole


# Fake people on a reserved domain (docs/domain.md: demo runs on fake data only).
DEMO_USERS = (
    DemoUser("calisan@example.com", "Ayşe Yılmaz", UserRole.EMPLOYEE),
    DemoUser("yonetici@example.com", "Mehmet Demir", UserRole.MANAGER),
    DemoUser("ik@example.com", "Zeynep Kaya", UserRole.HR),
)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _not_logged_in() -> UnauthorizedError:
    return UnauthorizedError(NOT_LOGGED_IN_MESSAGE, code=NOT_LOGGED_IN_CODE)


def _session_user(user: User, csrf_token: str) -> SessionUser:
    return SessionUser(
        id=user.id, name=user.name, email=user.email, role=user.role, csrf_token=csrf_token
    )


def authenticate(users: UserStore, email: str, password: str) -> User:
    """The user for these credentials; one and the same error for every failure (R-3)."""
    user = users.get_by_email(normalize_email(email))
    if user is None:
        # Same work as a real check, so timing does not tell which e-mails exist (plan R-4).
        verify_password(dummy_hash(), password)
        raise UnauthorizedError(INVALID_CREDENTIALS_MESSAGE, code=INVALID_CREDENTIALS_CODE)
    if not verify_password(user.password_hash, password):
        raise UnauthorizedError(INVALID_CREDENTIALS_MESSAGE, code=INVALID_CREDENTIALS_CODE)
    return user


def start_session(
    users: UserStore, email: str, password: str, clock: Clock, secret: str
) -> LoginResult:
    user = authenticate(users, email, password)
    csrf_token = secrets.token_urlsafe(32)
    token = sign(SessionToken(user_id=user.id, issued_at=clock.now(), csrf=csrf_token), secret)
    return LoginResult(token=token, user=_session_user(user, csrf_token))


def resolve_session(
    users: UserStore, raw_token: str | None, clock: Clock, secret: str
) -> SessionUser:
    """The session's user, or UnauthorizedError when absent, altered, expired or unknown (R-4)."""
    if not raw_token:
        raise _not_logged_in()
    token = verify(raw_token, secret)
    if token is None:
        raise _not_logged_in()
    age = clock.now() - token.issued_at
    # Invalid at exactly 8 hours and after (R-5); a token from the future is not trusted either.
    if age < timedelta(0) or age >= SESSION_DURATION:
        raise _not_logged_in()
    user = users.get_by_id(token.user_id)
    if user is None:
        raise _not_logged_in()
    return _session_user(user, token.csrf)


def check_csrf(session: SessionUser, presented: str | None) -> None:
    """State-changing requests must echo the session's CSRF token (R-7)."""
    if not presented or not hmac.compare_digest(
        presented.encode("utf-8"), session.csrf_token.encode("utf-8")
    ):
        raise ForbiddenError(CSRF_INVALID_MESSAGE, code=CSRF_INVALID_CODE)


def ensure_demo_users(users: UserStore, password: str) -> int:
    """Create the missing demo users; existing ones are left untouched. Returns how many were
    created (spec 0002, AC-7: idempotent)."""
    created = 0
    for demo in DEMO_USERS:
        if users.get_by_email(demo.email) is None:
            users.add(
                User(
                    email=demo.email,
                    name=demo.name,
                    role=demo.role,
                    password_hash=hash_password(password),
                )
            )
            created += 1
    return created


# Transaction-owning entry points for the API and the seed command (docs/architecture.md).


def log_in(database: Database, email: str, password: str, clock: Clock, secret: str) -> LoginResult:
    with database.session() as session:
        return start_session(UserRepository(session), email, password, clock, secret)


def current_user(
    database: Database, raw_token: str | None, clock: Clock, secret: str
) -> SessionUser:
    with database.session() as session:
        return resolve_session(UserRepository(session), raw_token, clock, secret)


def seed_demo_users(database: Database, password: str) -> int:
    with database.session() as session:
        return ensure_demo_users(UserRepository(session), password)
