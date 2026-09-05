"""
Domain-level exceptions and their mapping to HTTP responses.

Per the W1 architecture, `domain/` must not depend on FastAPI. These
exception classes are plain Python and live in `core/` (infrastructure),
while `domain/` code is free to raise them. The handlers registered here
are the only place that translates a domain error into an HTTP response —
individual route handlers never build error responses by hand.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class NexusError(Exception):
    """Base class for all NEXUS domain/application errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(NexusError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ValidationError(NexusError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "validation_error"


class ConflictError(NexusError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NexusError)
    async def handle_nexus_error(request: Request, exc: NexusError) -> JSONResponse:
        logger.warning("%s: %s (%s)", exc.error_code, exc.message, request.url.path)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.error_code, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error at %s", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred.",
            },
        )
