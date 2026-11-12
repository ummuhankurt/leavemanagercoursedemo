"""GET /api/v1/health — public status query (spec 0001; docs/security.md default-deny exception)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from leave_manager.core.db import Database
from leave_manager.services import health as health_service

router = APIRouter(prefix="/api/v1", tags=["health"])


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    version: str
    database: str


@router.get("/health", response_model=HealthResponse)
def read_health(request: Request) -> HealthResponse:
    database: Database = request.app.state.database
    result = health_service.check_health(database)
    return HealthResponse(status=result.status, version=result.version, database=result.database)
