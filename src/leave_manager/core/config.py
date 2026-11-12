"""Application settings, read from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

from leave_manager.core.errors import ConfigurationError

DATABASE_URL_ENV = "LEAVE_MANAGER_DATABASE_URL"
DEFAULT_DATABASE_URL = "sqlite:///./leave_manager.db"
SESSION_SECRET_ENV = "LEAVE_MANAGER_SESSION_SECRET"
COOKIE_SECURE_ENV = "LEAVE_MANAGER_COOKIE_SECURE"

_TRUE_VALUES = {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    # Signs session tokens; no default exists on purpose (spec 0002, R-10).
    session_secret: str
    # True in production: the session cookie is sent over HTTPS only (spec 0002, AC-6).
    cookie_secure: bool = False

    @classmethod
    def from_env(cls) -> Settings:
        secret = os.environ.get(SESSION_SECRET_ENV, "").strip()
        if not secret:
            # Names the variable, never a value (spec 0002, AC-10).
            raise ConfigurationError(
                f"{SESSION_SECRET_ENV} ortam değişkeni tanımlı değil; uygulama başlatılamaz."
            )
        return cls(
            database_url=os.environ.get(DATABASE_URL_ENV, DEFAULT_DATABASE_URL),
            session_secret=secret,
            cookie_secure=os.environ.get(COOKIE_SECURE_ENV, "").strip().lower() in _TRUE_VALUES,
        )
