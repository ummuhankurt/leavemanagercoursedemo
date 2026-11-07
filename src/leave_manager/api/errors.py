"""The single error handler (docs/conventions.md, Error handling)."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from leave_manager.core.errors import DomainError

logger = logging.getLogger(__name__)

INTERNAL_ERROR_CODE = "INTERNAL_ERROR"
INTERNAL_ERROR_MESSAGE = "Beklenmeyen bir hata oluştu."


def error_body(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


async def handle_domain_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    return JSONResponse(status_code=exc.status_code, content=error_body(exc.code, exc.message))


async def handle_unexpected_error(_request: Request, exc: Exception) -> JSONResponse:
    # Details go to the log only — never to the user.
    logger.exception("unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500, content=error_body(INTERNAL_ERROR_CODE, INTERNAL_ERROR_MESSAGE)
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
