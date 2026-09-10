import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


def _error_response(status_code: int, message: str, *, details=None, headers=None) -> JSONResponse:
    content = {"error": {"status_code": status_code, "message": message}}
    if details is not None:
        content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=content, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    """Wire up a consistent JSON error envelope and make sure nothing
    unhandled leaks a stack trace back to the client."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return _error_response(exc.status_code, str(exc.detail), headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Invalid request data",
            details=exc.errors(),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.warning("Database integrity error on %s: %s", request.url.path, exc)
        return _error_response(
            status.HTTP_409_CONFLICT,
            "Resource already exists or violates a database constraint",
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Unhandled database error on %s", request.url.path)
        return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "A database error occurred")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled server error on %s", request.url.path)
        return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred")
