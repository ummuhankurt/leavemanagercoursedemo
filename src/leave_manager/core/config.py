"""Application settings, read from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

DATABASE_URL_ENV = "LEAVE_MANAGER_DATABASE_URL"
DEFAULT_DATABASE_URL = "sqlite:///./leave_manager.db"


@dataclass(frozen=True)
class Settings:
    database_url: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(database_url=os.environ.get(DATABASE_URL_ENV, DEFAULT_DATABASE_URL))
