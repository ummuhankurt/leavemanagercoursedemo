"""ORM entities. Schema changes go through Alembic migrations only (docs/conventions.md)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Imported after Base so every entity is registered on Base.metadata.
from leave_manager.models.user import User, UserRole  # noqa: E402

__all__ = ["Base", "User", "UserRole"]
