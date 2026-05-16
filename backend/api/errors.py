from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.errors import (
    ConflictError,
    ExternalSourcePayloadError,
    ExternalSourceTimeoutError,
    ExternalSourceUnavailableError,
    NotFoundError,
    ValidationError,
)


def _problem(status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "detail": detail})


async def _not_found_handler(_: Request, exc: Exception) -> JSONResponse:
    return _problem(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


async def _conflict_handler(_: Request, exc: Exception) -> JSONResponse:
    return _problem(status.HTTP_409_CONFLICT, "conflict", str(exc))


async def _validation_handler(_: Request, exc: Exception) -> JSONResponse:
    return _problem(status.HTTP_400_BAD_REQUEST, "validation_error", str(exc))


async def _gateway_timeout_handler(_: Request, exc: Exception) -> JSONResponse:
    return _problem(status.HTTP_504_GATEWAY_TIMEOUT, "upstream_timeout", str(exc))


async def _bad_gateway_handler(_: Request, exc: Exception) -> JSONResponse:
    return _problem(status.HTTP_502_BAD_GATEWAY, "upstream_unavailable", str(exc))


async def _bad_gateway_payload_handler(_: Request, exc: Exception) -> JSONResponse:
    return _problem(status.HTTP_502_BAD_GATEWAY, "upstream_payload", str(exc))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, _not_found_handler)
    app.add_exception_handler(ConflictError, _conflict_handler)
    app.add_exception_handler(ValidationError, _validation_handler)
    app.add_exception_handler(ExternalSourceTimeoutError, _gateway_timeout_handler)
    app.add_exception_handler(ExternalSourceUnavailableError, _bad_gateway_handler)
    app.add_exception_handler(ExternalSourcePayloadError, _bad_gateway_payload_handler)
