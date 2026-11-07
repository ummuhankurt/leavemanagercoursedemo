"""User account and role (spec 0002, R-8)."""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from leave_manager.models import Base


class UserRole(StrEnum):
    EMPLOYEE = "Employee"
    MANAGER = "Manager"
    HR = "HR"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Stored normalized (trimmed, lower case) — comparison is case-insensitive (spec 0002, R-2).
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda roles: [role.value for role in roles],
        )
    )
