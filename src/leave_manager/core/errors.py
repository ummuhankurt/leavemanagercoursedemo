"""Domain error types (docs/conventions.md, Error handling).

Services raise these; the API layer's single handler turns them into
``{"error": {"code": ..., "message": ...}}`` with the class's HTTP status.
"""

from __future__ import annotations


class DomainError(Exception):
    status_code = 400
    code = "DOMAIN_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class ValidationError(DomainError):
    status_code = 422
    code = "VALIDATION_ERROR"


class NotFoundError(DomainError):
    status_code = 404
    code = "NOT_FOUND"


class ForbiddenError(DomainError):
    status_code = 403
    code = "FORBIDDEN"


class ConflictError(DomainError):
    status_code = 409
    code = "CONFLICT"


class ServiceUnavailableError(DomainError):
    status_code = 503
    code = "SERVICE_UNAVAILABLE"


class DatabaseUnavailableError(Exception):
    """Infrastructure failure raised by repositories; never shown to users as is."""
