from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine


EXPECTED_ALEMBIC_HEAD = "0006_owner_isolation"

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
        }


async def get_runtime_schema_report() -> RuntimeSchemaReport:
    if settings.environment == "test":
        return RuntimeSchemaReport("skipped", None, EXPECTED_ALEMBIC_HEAD, None, [])
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
    report = await get_runtime_schema_report()
    if report.drift and (settings.runtime_schema_strict if strict is None else strict):
        details = "; ".join(item.message() for item in report.drift)
        raise RuntimeError(f"Runtime PostgreSQL schema drift detected: {details}")
    return report
