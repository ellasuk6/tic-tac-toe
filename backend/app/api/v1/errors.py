"""Turn every error into the constitution's envelope: {"code": ..., "detail": ...}.

This is the only place that decides status codes for domain errors:
  NotFoundError      -> 404
  RuleViolationError -> 409  (a business rule refused the request)
  bad request body   -> 422  (failed schema validation)
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import DomainError, NotFoundError, RuleViolationError

_STATUS_FOR_DOMAIN_ERROR: list[tuple[type[DomainError], int]] = [
    (NotFoundError, 404),
    (RuleViolationError, 409),
]

_CODE_FOR_HTTP_STATUS = {404: "not_found", 405: "method_not_allowed"}


def _envelope(status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "detail": detail})


async def handle_domain_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    status_code = next(
        (status for kind, status in _STATUS_FOR_DOMAIN_ERROR if isinstance(exc, kind)), 500
    )
    return _envelope(status_code, exc.code, exc.detail)


async def handle_validation_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    problems = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        problems.append(f"{location}: {error['msg']}" if location else str(error["msg"]))
    return _envelope(422, "validation_error", "; ".join(problems) + ".")


async def handle_http_error(_request: Request, exc: Exception) -> JSONResponse:
    # Framework-level errors, e.g. a URL that matches no route.
    assert isinstance(exc, StarletteHTTPException)
    code = _CODE_FOR_HTTP_STATUS.get(exc.status_code, "http_error")
    return _envelope(exc.status_code, code, str(exc.detail))


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
