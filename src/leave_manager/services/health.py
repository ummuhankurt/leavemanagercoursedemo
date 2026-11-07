"""System status: running, version, database reachability (spec 0001, R-1/R-2)."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from typing import Protocol

from leave_manager.core.db import Database
from leave_manager.core.errors import DatabaseUnavailableError, ServiceUnavailableError
from leave_manager.repositories.health import HealthRepository

# The single source of the version is pyproject.toml (spec 0001, G-3).
DISTRIBUTION_NAME = "leave-manager"

STATUS_OK = "ok"
DATABASE_REACHABLE = "reachable"
UNAVAILABLE_MESSAGE = "Hizmet şu anda kullanılamıyor."


class DatabaseProbe(Protocol):
    def ping(self) -> None: ...


@dataclass(frozen=True)
class HealthStatus:
    status: str
    version: str
    database: str


def app_version() -> str:
    return metadata.version(DISTRIBUTION_NAME)


def get_status(probe: DatabaseProbe, version: str) -> HealthStatus:
    try:
        probe.ping()
    except DatabaseUnavailableError as exc:
        raise ServiceUnavailableError(UNAVAILABLE_MESSAGE) from exc
    return HealthStatus(status=STATUS_OK, version=version, database=DATABASE_REACHABLE)


def check_health(database: Database) -> HealthStatus:
    with database.session() as session:
        return get_status(HealthRepository(session), app_version())
