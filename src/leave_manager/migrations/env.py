"""Alembic environment: the only path for schema changes (docs/conventions.md, Data rules)."""

from __future__ import annotations

import os

from alembic import context
from sqlalchemy import create_engine, pool

from leave_manager.core.config import DATABASE_URL_ENV, DEFAULT_DATABASE_URL
from leave_manager.models import Base

config = context.config
target_metadata = Base.metadata


def _database_url() -> str:
    # Set programmatically by core.db.migrate; from the environment when run as `alembic upgrade`.
    configured = config.get_main_option("sqlalchemy.url")
    return configured or os.environ.get(DATABASE_URL_ENV, DEFAULT_DATABASE_URL)


def run_migrations_offline() -> None:
    context.configure(url=_database_url(), target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_database_url(), poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            # Batch mode: SQLite cannot ALTER most columns in place.
            context.configure(
                connection=connection, target_metadata=target_metadata, render_as_batch=True
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
