"""Database engine and sessions. The transaction boundary is opened by the service layer."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def _enable_sqlite_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
    # Known trap: SQLite ships with foreign keys off (docs/conventions.md, Known traps).
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Database:
    """Owns the engine; hands out one session per unit of work."""

    def __init__(self, url: str) -> None:
        self._engine: Engine = create_engine(url)
        if self._engine.dialect.name == "sqlite":
            event.listen(self._engine, "connect", _enable_sqlite_foreign_keys)
        self._sessions = sessionmaker(bind=self._engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        """One transaction: committed on success, rolled back on any exception."""
        with self._sessions() as session, session.begin():
            yield session

    def dispose(self) -> None:
        self._engine.dispose()
