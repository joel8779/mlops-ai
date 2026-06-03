from dataclasses import asdict, dataclass
import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.logging import get_logger
from app.core.config import settings
from app.db.session import engine


EXPECTED_ALEMBIC_HEAD = "0010_composite_indexes"
SCHEMA_REPORT_CACHE_SECONDS = 30
logger = get_logger(__name__)
_cached_schema_report: tuple[float, "RuntimeSchemaReport"] | None = None

CRITICAL_COLUMNS: dict[str, set[str]] = {
    "ats_scores": {
        "id",
        "organization_id",
        "owner_id",
        "candidate_id",
        "job_description_id",
        "resume_id",
        "ats_score",
        "components",
        "issues",
        "recommendations",
        "explanation",
        "scoring_version",
        "created_at",
        "updated_at",
        "deleted_at",
    },
    "candidate_matches": {"organization_id", "owner_id", "candidate_id", "job_description_id", "overall_score", "semantic_score"},
    "candidate_pipeline_stages": {"organization_id", "owner_id", "candidate_id", "job_description_id", "stage"},
    "ranking_feedback": {"organization_id", "owner_id", "candidate_id", "job_description_id", "action"},
    "candidate_embeddings": {"organization_id", "owner_id", "candidate_id", "resume_id", "qdrant_point_id"},
    "resumes": {"id", "organization_id", "owner_id", "candidate_id"},
}

CRITICAL_FOREIGN_KEYS: dict[str, set[str]] = {
    "ats_scores": {"candidate_id", "job_description_id", "resume_id"},
    "candidate_matches": {"candidate_id", "job_description_id"},
    "candidate_pipeline_stages": {"candidate_id", "job_description_id"},
    "ranking_feedback": {"candidate_id", "job_description_id"},
}


@dataclass(frozen=True)
class SchemaDrift:
    table: str
    issue: str
    detail: str

    def message(self) -> str:
        return f"{self.table}: {self.issue} ({self.detail})"


@dataclass(frozen=True)
class RuntimeSchemaReport:
    status: str
    dialect: str | None
    expected_revision: str
    current_revision: str | None
    drift: list[SchemaDrift]
    error: str | None = None

    @property
    def ready(self) -> bool:
        return self.status == "healthy"

    def model_dump(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "dialect": self.dialect,
            "expected_revision": self.expected_revision,
            "current_revision": self.current_revision,
            "drift": [asdict(item) | {"message": item.message()} for item in self.drift],
            "error": self.error,
        }


async def get_runtime_schema_report(use_cache: bool = True) -> RuntimeSchemaReport:
    global _cached_schema_report
    if settings.environment == "test":
        return RuntimeSchemaReport("skipped", None, EXPECTED_ALEMBIC_HEAD, None, [])

    now = time.monotonic()
    if use_cache and _cached_schema_report is not None:
        cached_at, cached_report = _cached_schema_report
        if now - cached_at < SCHEMA_REPORT_CACHE_SECONDS:
            return cached_report

    try:
        report = await _inspect_runtime_schema()
    except SQLAlchemyError as exc:
        logger.exception("runtime_schema_validation_failed", error=str(exc))
        report = RuntimeSchemaReport(
            status="validation_error",
            dialect=None,
            expected_revision=EXPECTED_ALEMBIC_HEAD,
            current_revision=None,
            drift=[],
            error=str(exc),
        )

    _cached_schema_report = (now, report)
    if report.drift:
        logger.warning(
            "runtime_schema_drift_detected",
            current_revision=report.current_revision,
            expected_revision=report.expected_revision,
            drift=[item.message() for item in report.drift],
        )
    elif report.error:
        logger.warning("runtime_schema_unhealthy", error=report.error)
    return report


async def _inspect_runtime_schema() -> RuntimeSchemaReport:
    async with engine.connect() as connection:
        if connection.dialect.name != "postgresql":
            return RuntimeSchemaReport(
                "skipped",
                connection.dialect.name,
                EXPECTED_ALEMBIC_HEAD,
                None,
                [],
            )

        drift: list[SchemaDrift] = []
        version = await connection.scalar(text("SELECT version_num FROM alembic_version LIMIT 1"))
        if version != EXPECTED_ALEMBIC_HEAD:
            drift.append(
                SchemaDrift(
                    "alembic_version",
                    "unexpected revision",
                    f"expected {EXPECTED_ALEMBIC_HEAD}, found {version or 'none'}",
                )
            )

        for table, expected_columns in CRITICAL_COLUMNS.items():
            existing_columns = {
                row[0]
                for row in (
                    await connection.execute(
                        text(
                            """
                            SELECT column_name
                            FROM information_schema.columns
                            WHERE table_schema = 'public' AND table_name = :table_name
                            """
                        ),
                        {"table_name": table},
                    )
                ).all()
            }
            missing_columns = sorted(expected_columns - existing_columns)
            if not existing_columns:
                drift.append(SchemaDrift(table, "missing table", "table is absent from public schema"))
            if missing_columns:
                drift.append(
                    SchemaDrift(table, "missing columns", ", ".join(missing_columns))
                )

        for table, expected_fk_columns in CRITICAL_FOREIGN_KEYS.items():
            existing_fk_columns = {
                row[0]
                for row in (
                    await connection.execute(
                        text(
                            """
                            SELECT kcu.column_name
                            FROM information_schema.table_constraints tc
                            JOIN information_schema.key_column_usage kcu
                              ON tc.constraint_name = kcu.constraint_name
                             AND tc.table_schema = kcu.table_schema
                            WHERE tc.constraint_type = 'FOREIGN KEY'
                              AND tc.table_schema = 'public'
                              AND tc.table_name = :table_name
                            """
                        ),
                        {"table_name": table},
                    )
                ).all()
            }
            missing_fk_columns = sorted(expected_fk_columns - existing_fk_columns)
            if missing_fk_columns:
                drift.append(
                    SchemaDrift(table, "missing foreign keys", ", ".join(missing_fk_columns))
                )

        return RuntimeSchemaReport(
            "drift_detected" if drift else "healthy",
            connection.dialect.name,
            EXPECTED_ALEMBIC_HEAD,
            str(version) if version else None,
            drift,
        )


async def validate_runtime_schema(strict: bool | None = None) -> RuntimeSchemaReport:
    report = await get_runtime_schema_report(use_cache=False)
    if report.drift and (settings.runtime_schema_strict if strict is None else strict):
        details = "; ".join(item.message() for item in report.drift)
        raise RuntimeError(f"Runtime PostgreSQL schema drift detected: {details}")
    if report.error and (settings.runtime_schema_strict if strict is None else strict):
        raise RuntimeError(f"Runtime PostgreSQL schema validation failed: {report.error}")
    return report
