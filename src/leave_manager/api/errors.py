"""The single error handler (docs/conventions.md, Error handling)."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from leave_manager.api.security_headers import SECURITY_HEADERS
from leave_manager.core.errors import DomainError

logger = logging.getLogger(__name__)

INTERNAL_ERROR_CODE = "INTERNAL_ERROR"
INTERNAL_ERROR_MESSAGE = "Beklenmeyen bir hata oluştu."
VALIDATION_ERROR_CODE = "VALIDATION_ERROR"
VALIDATION_ERROR_MESSAGE = "Geçersiz istek."

# Framework errors in the project's own words (backlog B-1, spec 0002 R-12).
_HTTP_ERRORS: dict[int, tuple[str, str]] = {
    404: ("NOT_FOUND", "Kaynak bulunamadı."),
    405: ("METHOD_NOT_ALLOWED", "Bu yöntem desteklenmiyor."),
}
_HTTP_ERROR_FALLBACK = ("HTTP_ERROR", "İstek işlenemedi.")


def error_body(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


async def handle_domain_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    return JSONResponse(status_code=exc.status_code, content=error_body(exc.code, exc.message))


async def handle_http_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code, message = _HTTP_ERRORS.get(exc.status_code, _HTTP_ERROR_FALLBACK)
    # Keep framework headers such as Allow on 405.
    return JSONResponse(
        status_code=exc.status_code, content=error_body(code, message), headers=exc.headers
    )


async def handle_validation_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    # Location and type only: the rejected input may hold a password (plan 0002, R-7).
    logger.info("request validation failed: %s", [(e["loc"], e["type"]) for e in exc.errors()])
    return JSONResponse(
        status_code=422, content=error_body(VALIDATION_ERROR_CODE, VALIDATION_ERROR_MESSAGE)
    )


async def handle_unexpected_error(_request: Request, exc: Exception) -> JSONResponse:
    # Details go to the log only — never to the user.
    logger.exception("unhandled error", exc_info=exc)
    # Starlette runs this handler in ServerErrorMiddleware, outside every app middleware, so the
    # security headers are added here as well (spec 0002, R-13; review round 1 M-1).
    return JSONResponse(
        status_code=500,
        content=error_body(INTERNAL_ERROR_CODE, INTERNAL_ERROR_MESSAGE),
        headers=SECURITY_HEADERS,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
