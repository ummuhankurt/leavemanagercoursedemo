"""Composition root. Run locally: ``uv run uvicorn leave_manager.main:create_app --factory``."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.routing import Match, Mount
from starlette.types import Scope

from leave_manager.api import auth, health
from leave_manager.api.errors import register_error_handlers
from leave_manager.api.security_headers import add_security_headers
from leave_manager.core.clock import Clock, SystemClock
from leave_manager.core.config import Settings
from leave_manager.core.db import Database
from leave_manager.services.health import app_version

STATIC_DIR = Path(__file__).parent / "static"
API_PREFIX = "/api/"


class StaticMount(Mount):
    """Serves static files everywhere except under /api/, so unknown API paths and wrong methods
    get the router's own 404 / 405 instead of a static-file 404 (spec 0002, AC-8)."""

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        if str(scope.get("path", "")).startswith(API_PREFIX):
            return Match.NONE, {}
        return super().matches(scope)


def create_app(settings: Settings | None = None, clock: Clock | None = None) -> FastAPI:
    # Raises ConfigurationError without a session secret: the app does not start (spec 0002, R-10).
    settings = settings or Settings.from_env()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        database.dispose()

    app = FastAPI(title="Leave Manager", version=app_version(), lifespan=lifespan)
    app.state.settings = settings
    app.state.clock = clock or SystemClock()
    app.state.database = database
    register_error_handlers(app)
    add_security_headers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    # Added last so /api routes always win over static files.
    app.router.routes.append(
        StaticMount("/", app=StaticFiles(directory=STATIC_DIR, html=True), name="static")
    )
    return app
