"""User queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from leave_manager.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        """Exact match on the stored (already normalized) e-mail."""
        return self._session.scalars(select(User).where(User.email == email)).one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        return self._session.get(User, user_id)

    def add(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()
        return user
