"""add owner scoped recruiter data isolation

Revision ID: 0006_owner_isolation
Revises: 0005_pipeline_stage_contract
Create Date: 2026-05-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_owner_isolation"
down_revision: str | None = "0005_pipeline_stage_contract"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


OWNER_TABLES = [
    "candidates",
    "resumes",
    "job_descriptions",
    "job_description_embeddings",
    "candidate_embeddings",
    "candidate_skills",
    "recruiter_notes",
    "candidate_pipeline_stages",
    "candidate_bookmarks",
    "recruiter_activities",
    "candidate_matches",
    "ranking_feedback",
    "analytics_snapshots",
    "ats_scores",
    "resume_processing_events",
]


def upgrade() -> None:
    _clear_operational_data()
    for table_name in OWNER_TABLES:
        op.add_column(table_name, sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False))
        op.create_index(f"ix_{table_name}_owner_id", table_name, ["owner_id"])
        op.create_foreign_key(
            f"fk_{table_name}_owner_id_users",
            table_name,
            "users",
            ["owner_id"],
            ["id"],
            ondelete="CASCADE",
        )
    op.add_column("llm_usage_logs", sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_llm_usage_logs_owner_id", "llm_usage_logs", ["owner_id"])
    op.create_foreign_key(
        "fk_llm_usage_logs_owner_id_users",
        "llm_usage_logs",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_candidates_owner_created", "candidates", ["owner_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_candidates_owner_created", table_name="candidates")
    op.drop_constraint("fk_llm_usage_logs_owner_id_users", "llm_usage_logs", type_="foreignkey")
    op.drop_index("ix_llm_usage_logs_owner_id", table_name="llm_usage_logs")
    op.drop_column("llm_usage_logs", "owner_id")
    for table_name in reversed(OWNER_TABLES):
        op.drop_constraint(f"fk_{table_name}_owner_id_users", table_name, type_="foreignkey")
        op.drop_index(f"ix_{table_name}_owner_id", table_name=table_name)
        op.drop_column(table_name, "owner_id")


def _clear_operational_data() -> None:
    for table_name in [
        "resume_processing_events",
        "ats_scores",
        "ranking_feedback",
        "candidate_matches",
        "candidate_bookmarks",
        "candidate_pipeline_stages",
        "recruiter_notes",
        "candidate_skills",
        "candidate_embeddings",
        "job_description_embeddings",
        "recruiter_activities",
        "analytics_snapshots",
        "llm_usage_logs",
        "resumes",
        "job_descriptions",
        "candidates",
    ]:
        op.execute(sa.text(f"DELETE FROM {table_name}"))
