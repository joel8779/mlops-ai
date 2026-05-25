from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import traceback

from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from app.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        db_trace = _sqlalchemy_trace(exc)
        logger.exception("database_error", path=request.url.path, db_trace=db_trace)
        raw = str(getattr(exc, "orig", exc))
        if isinstance(exc, IntegrityError):
            lowered = raw.lower()
            if "foreign key" in lowered:
                detail = {
                    "message": "Related recruiting record was not found.",
                    "code": "database_foreign_key_violation",
                    "next_action": "Refresh the candidate/job context and retry the operation.",
                }
            elif "not null" in lowered or "null value" in lowered:
                detail = {
                    "message": "A required recruiting field was missing.",
                    "code": "database_required_field_missing",
                    "next_action": "Check extracted candidate/job fields and retry after processing completes.",
                }
            elif "unique" in lowered or "duplicate" in lowered:
                detail = {
                    "message": "This recruiting relationship already exists.",
                    "code": "database_duplicate_relationship",
                    "next_action": "Refresh the page; the existing record can be reused.",
                }
            else:
                detail = {
                    "message": "This record conflicts with existing recruiting data.",
                    "code": "database_integrity_error",
                    "next_action": "Check duplicate records or missing candidate/job relationships.",
                }
            status_code = status.HTTP_409_CONFLICT
        elif isinstance(exc, OperationalError):
            detail = {
                "message": "The database is unavailable or still starting.",
                "code": "database_unavailable",
                "next_action": "Wait for PostgreSQL readiness, then retry.",
            }
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            detail = {
                "message": "The database rejected this operation.",
                "code": "database_operation_failed",
                "next_action": "Check backend logs for the exact SQLAlchemy exception and verify related records exist.",
            }
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(
            status_code=status_code,
            content={"detail": {**detail, "trace": db_trace}},
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


def _sqlalchemy_trace(exc: SQLAlchemyError) -> dict:
    orig = getattr(exc, "orig", None)
    statement = str(getattr(exc, "statement", "") or "")
    params = getattr(exc, "params", None)
    diag = getattr(orig, "diag", None)
    table = getattr(diag, "table_name", None) if diag else None
    constraint = getattr(diag, "constraint_name", None) if diag else None
    schema = getattr(diag, "schema_name", None) if diag else None
    relation = getattr(diag, "column_name", None) if diag else None
    return {
        "exception_type": type(exc).__name__,
        "driver_exception_type": type(orig).__name__ if orig else None,
        "table": table,
        "schema": schema,
        "relation": relation,
        "constraint": constraint,
        "statement": _redact_statement(statement),
        "params_summary": _params_summary(params),
        "stack": traceback.format_exc(limit=8),
    }


def _redact_statement(statement: str) -> str:
    compact = " ".join(statement.split())
    return compact[:1200]


def _params_summary(params) -> dict | list | str | None:
    if params is None:
        return None
    if isinstance(params, dict):
        return {key: _safe_value(value) for key, value in params.items()}
    if isinstance(params, (list, tuple)):
        return [_safe_value(value) for value in list(params)[:20]]
    return str(params)[:500]


def _safe_value(value):
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if len(text) > 160:
        return f"{text[:160]}..."
    return text
