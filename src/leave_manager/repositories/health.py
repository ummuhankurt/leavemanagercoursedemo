"""Database reachability probe."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from leave_manager.core.errors import DatabaseUnavailableError


class HealthRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def ping(self) -> None:
        """Run a trivial query; raise DatabaseUnavailableError when the database is unreachable."""
        try:
            self._session.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise DatabaseUnavailableError("database unreachable") from exc
