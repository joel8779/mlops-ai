"""ai intelligence and recruiter workflow

Revision ID: 0002_ai_intelligence_workflow
Revises: 0001_initial_schema
Create Date: 2026-05-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_ai_intelligence_workflow"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def base_columns() -> list[sa.Column]:
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    job_status = postgresql.ENUM("draft", "active", "closed", name="jobstatus")
    pipeline_stage = postgresql.ENUM(
        "Applied",
        "Screening",
        "Interview",
        "Technical Round",
        "Final Round",
        "Hired",
        "Rejected",
        name="pipelinestage",
        create_type=False,
    )
    job_status.create(op.get_bind(), checkfirst=True)
    pipeline_stage.create(op.get_bind(), checkfirst=True)

    op.add_column("job_descriptions", sa.Column("status", job_status, nullable=False, server_default="draft"))
    op.add_column("job_descriptions", sa.Column("role_category", sa.String(150), nullable=True))
    op.add_column("job_descriptions", sa.Column("years_experience_min", sa.Integer(), nullable=True))
    op.add_column("job_descriptions", sa.Column("years_experience_max", sa.Integer(), nullable=True))
    op.add_column("job_descriptions", sa.Column("education_requirements", postgresql.JSONB(), nullable=False, server_default="[]"))
    op.add_column("job_descriptions", sa.Column("keywords", postgresql.JSONB(), nullable=False, server_default="[]"))
    op.create_index("ix_job_descriptions_status", "job_descriptions", ["status"])
    op.create_index("ix_job_descriptions_role_category", "job_descriptions", ["role_category"])

    op.create_table(
        "job_description_embeddings",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("qdrant_point_id", sa.String(120), nullable=False),
        sa.Column("model_name", sa.String(255), nullable=False),
        sa.Column("vector_size", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["job_description_id"], ["job_descriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("qdrant_point_id"),
        sa.UniqueConstraint("job_description_id", "chunk_index", name="uq_jd_embeddings_jd_chunk"),
    )
    op.create_index("ix_job_description_embeddings_job_description_id", "job_description_embeddings", ["job_description_id"])
    op.create_index("ix_job_description_embeddings_qdrant_point_id", "job_description_embeddings", ["qdrant_point_id"])

    op.create_table(
        "candidate_pipeline_stages",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("stage", pipeline_stage, nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["job_description_id"], ["job_descriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_pipeline_stages_stage", "candidate_pipeline_stages", ["stage"])

    op.create_table(
        "candidate_bookmarks",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", "user_id", name="uq_candidate_bookmark_user"),
    )

    op.create_table(
        "recruiter_activities",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("activity_type", sa.String(100), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["job_description_id"], ["job_descriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recruiter_activities_activity_type", "recruiter_activities", ["activity_type"])

    op.create_table(
        "candidate_matches",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("semantic_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("skill_match", sa.Numeric(6, 2), nullable=False),
        sa.Column("experience_match", sa.Numeric(6, 2), nullable=False),
        sa.Column("education_match", sa.Numeric(6, 2), nullable=False),
        sa.Column("keyword_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("matched_skills", postgresql.JSONB(), nullable=False),
        sa.Column("missing_skills", postgresql.JSONB(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("scoring_version", sa.String(64), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["job_description_id"], ["job_descriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", "job_description_id", name="uq_candidate_match_job"),
    )
    op.create_index("ix_candidate_matches_job_score", "candidate_matches", ["job_description_id", "overall_score"])

    op.create_table(
        "ats_scores",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ats_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("issues", postgresql.JSONB(), nullable=False),
        sa.Column("recommendations", postgresql.JSONB(), nullable=False),
        sa.Column("scoring_version", sa.String(64), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ats_scores_ats_score", "ats_scores", ["ats_score"])

    op.create_table(
        "llm_usage_logs",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("feature", sa.String(100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost_usd", sa.Numeric(10, 6), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    for table in [
        "llm_usage_logs",
        "ats_scores",
        "candidate_matches",
        "recruiter_activities",
        "candidate_bookmarks",
        "candidate_pipeline_stages",
        "job_description_embeddings",
    ]:
        op.drop_table(table)
    op.drop_index("ix_job_descriptions_role_category", table_name="job_descriptions")
    op.drop_index("ix_job_descriptions_status", table_name="job_descriptions")
    for column in [
        "keywords",
        "education_requirements",
        "years_experience_max",
        "years_experience_min",
        "role_category",
        "status",
    ]:
        op.drop_column("job_descriptions", column)
    postgresql.ENUM(name="pipelinestage").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="jobstatus").drop(op.get_bind(), checkfirst=True)
