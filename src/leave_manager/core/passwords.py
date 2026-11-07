"""Password hashing with argon2 (docs/security.md, AuthN)."""

from __future__ import annotations

from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


@cache
def dummy_hash() -> str:
    """A hash no password matches in practice; verified for unknown e-mails so the response time
    does not reveal which e-mails exist (plan 0002, R-4)."""
    return _hasher.hash("unused-dummy-password-for-timing")
