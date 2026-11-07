"""Composition root. Run locally: ``uv run uvicorn leave_manager.main:create_app --factory``."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from leave_manager.api import health
from leave_manager.api.errors import register_error_handlers
from leave_manager.core.config import Settings
from leave_manager.core.db import Database
from leave_manager.services.health import app_version


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        database.dispose()

    app = FastAPI(title="Leave Manager", version=app_version(), lifespan=lifespan)
    app.state.database = database
    register_error_handlers(app)
    app.include_router(health.router)
    return app
