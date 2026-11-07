"""Session endpoints (spec 0002). The API only carries the session to the service layer;
every decision about it is made in services/auth.py (docs/security.md, AuthZ)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from leave_manager.core.clock import Clock
from leave_manager.core.config import Settings
from leave_manager.core.db import Database
from leave_manager.services import auth as auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SESSION_COOKIE = "lm_session"
CSRF_HEADER = "X-CSRF-Token"
SESSION_MAX_AGE_SECONDS = int(auth_service.SESSION_DURATION.total_seconds())


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=1024)

    @field_validator("email")
    @classmethod
    def email_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("email is blank")
        return value


class SessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    email: str
    role: str
    # Echoed in the X-CSRF-Token header of state-changing requests (spec 0002, R-7).
    csrf_token: str


def _settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def _clock(request: Request) -> Clock:
    clock: Clock = request.app.state.clock
    return clock


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


def current_session(request: Request) -> auth_service.SessionUser:
    """The logged-in user; 401 otherwise. Every protected endpoint depends on this."""
    return auth_service.current_user(
        _database(request),
        request.cookies.get(SESSION_COOKIE),
        _clock(request),
        _settings(request).session_secret,
    )


CurrentSession = Annotated[auth_service.SessionUser, Depends(current_session)]


def _response(user: auth_service.SessionUser) -> SessionResponse:
    return SessionResponse(
        name=user.name, email=user.email, role=user.role.value, csrf_token=user.csrf_token
    )


@router.post("/login", response_model=SessionResponse)
def log_in(body: LoginRequest, request: Request, response: Response) -> SessionResponse:
    # No CSRF token here: there is no session yet and the cookie is SameSite=Lax (R-7).
    settings = _settings(request)
    result = auth_service.log_in(
        _database(request), body.email, body.password, _clock(request), settings.session_secret
    )
    # A new login simply replaces whatever session cookie the browser had (R-1).
    response.set_cookie(
        SESSION_COOKIE,
        result.token,
        max_age=SESSION_MAX_AGE_SECONDS,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    return _response(result.user)


@router.get("/me", response_model=SessionResponse)
def read_me(session: CurrentSession) -> SessionResponse:
    return _response(session)


@router.post("/logout", status_code=204)
def log_out(
    session: CurrentSession,
    request: Request,
    csrf_token: Annotated[str | None, Header(alias=CSRF_HEADER)] = None,
) -> Response:
    auth_service.check_csrf(session, csrf_token)
    response = Response(status_code=204)
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_settings(request).cookie_secure,
    )
    return response
