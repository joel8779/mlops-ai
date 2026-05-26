"""job context ats scores

Revision ID: 0004_job_context_ats
Revises: 0003_enterprise_scale
Create Date: 2026-05-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_job_context_ats"
down_revision: str | None = "0003_enterprise_scale"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("ats_scores")}
    constraints = {constraint["name"] for constraint in inspector.get_foreign_keys("ats_scores")}
    uniques = {constraint["name"] for constraint in inspector.get_unique_constraints("ats_scores")}
    indexes = {index["name"] for index in inspector.get_indexes("ats_scores")}

    if "candidate_id" not in columns:
        op.add_column("ats_scores", sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=True))
    if "job_description_id" not in columns:
        op.add_column("ats_scores", sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=True))
    if "components" not in columns:
        op.add_column("ats_scores", sa.Column("components", postgresql.JSONB(), nullable=False, server_default="[]"))
    if "explanation" not in columns:
        op.add_column("ats_scores", sa.Column("explanation", sa.Text(), nullable=True))

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ats_score_migration_archive (
            source_ats_score_id uuid PRIMARY KEY,
            archived_at timestamptz NOT NULL DEFAULT now(),
            organization_id uuid NOT NULL,
            resume_id uuid NOT NULL,
            candidate_id uuid NULL,
            job_description_id uuid NULL,
            ats_score numeric(6, 2) NOT NULL,
            issues jsonb NOT NULL,
            recommendations jsonb NOT NULL,
            components jsonb NULL,
            explanation text NULL,
            scoring_version varchar(64) NOT NULL,
            created_at timestamptz NULL,
            updated_at timestamptz NULL,
            deleted_at timestamptz NULL,
            archive_reason varchar(120) NOT NULL
        )
        """
    )

    if "fk_ats_scores_candidate_id_candidates" not in constraints:
        op.create_foreign_key("fk_ats_scores_candidate_id_candidates", "ats_scores", "candidates", ["candidate_id"], ["id"])
    if "fk_ats_scores_job_description_id_job_descriptions" not in constraints:
        op.create_foreign_key(
            "fk_ats_scores_job_description_id_job_descriptions",
            "ats_scores",
            "job_descriptions",
            ["job_description_id"],
            ["id"],
        )
    op.execute(
        """
        UPDATE ats_scores
        SET candidate_id = resumes.candidate_id
        FROM resumes
        WHERE ats_scores.resume_id = resumes.id
          AND ats_scores.candidate_id IS NULL
          AND resumes.candidate_id IS NOT NULL
        """
    )
    op.execute(
        """
        WITH best_match AS (
            SELECT DISTINCT ON (candidate_id)
                candidate_id,
                job_description_id,
                overall_score,
                explanation
            FROM candidate_matches
            ORDER BY candidate_id, overall_score DESC, updated_at DESC, created_at DESC
        )
        UPDATE ats_scores
        SET job_description_id = best_match.job_description_id,
            explanation = COALESCE(ats_scores.explanation, best_match.explanation),
            scoring_version = 'ats-job-context-v1'
        FROM best_match
        WHERE ats_scores.candidate_id = best_match.candidate_id
          AND ats_scores.job_description_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE ats_scores
        SET components = COALESCE(components, '[]'::jsonb)
            || jsonb_build_array(
                jsonb_build_object(
                    'name', 'legacy_resume_ats_score',
                    'score', ats_score,
                    'evidence', jsonb_build_array('Migrated from resume-scoped ATS score'),
                    'weight', 0
                )
            )
        WHERE NOT EXISTS (
            SELECT 1
            FROM jsonb_array_elements(COALESCE(components, '[]'::jsonb)) AS component
            WHERE component->>'name' = 'legacy_resume_ats_score'
        )
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                row_number() OVER (
                    PARTITION BY candidate_id, job_description_id
                    ORDER BY updated_at DESC, created_at DESC, id
                ) AS row_number
            FROM ats_scores
            WHERE candidate_id IS NOT NULL AND job_description_id IS NOT NULL
        )
        INSERT INTO ats_score_migration_archive (
            source_ats_score_id,
            organization_id,
            resume_id,
            candidate_id,
            job_description_id,
            ats_score,
            issues,
            recommendations,
            components,
            explanation,
            scoring_version,
            created_at,
            updated_at,
            deleted_at,
            archive_reason
        )
        SELECT
            ats_scores.id,
            ats_scores.organization_id,
            ats_scores.resume_id,
            ats_scores.candidate_id,
            ats_scores.job_description_id,
            ats_scores.ats_score,
            ats_scores.issues,
            ats_scores.recommendations,
            ats_scores.components,
            ats_scores.explanation,
            ats_scores.scoring_version,
            ats_scores.created_at,
            ats_scores.updated_at,
            ats_scores.deleted_at,
            'duplicate_candidate_job'
        FROM ats_scores
        JOIN ranked ON ranked.id = ats_scores.id
        WHERE ranked.row_number > 1
        ON CONFLICT (source_ats_score_id) DO NOTHING
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                row_number() OVER (
                    PARTITION BY candidate_id, job_description_id
                    ORDER BY updated_at DESC, created_at DESC, id
                ) AS row_number
            FROM ats_scores
            WHERE candidate_id IS NOT NULL AND job_description_id IS NOT NULL
        )
        DELETE FROM ats_scores
        USING ranked
        WHERE ats_scores.id = ranked.id AND ranked.row_number > 1
        """
    )
    missing_context = bind.execute(
        sa.text("SELECT count(*) FROM ats_scores WHERE candidate_id IS NULL OR job_description_id IS NULL")
    ).scalar_one()
    duplicate_context = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM (
                SELECT candidate_id, job_description_id
                FROM ats_scores
                WHERE candidate_id IS NOT NULL AND job_description_id IS NOT NULL
                GROUP BY candidate_id, job_description_id
                HAVING count(*) > 1
            ) duplicates
            """
        )
    ).scalar_one()
    if missing_context == 0:
        op.alter_column("ats_scores", "candidate_id", nullable=False)
        op.alter_column("ats_scores", "job_description_id", nullable=False)
    if missing_context == 0 and duplicate_context == 0 and "uq_ats_score_candidate_job" not in uniques:
        op.create_unique_constraint("uq_ats_score_candidate_job", "ats_scores", ["candidate_id", "job_description_id"])
    if "ix_ats_scores_job_score" not in indexes:
        op.create_index("ix_ats_scores_job_score", "ats_scores", ["job_description_id", "ats_score"])
    op.alter_column("ats_scores", "components", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_ats_scores_job_score", table_name="ats_scores")
    op.drop_constraint("uq_ats_score_candidate_job", "ats_scores", type_="unique")
    op.drop_constraint("fk_ats_scores_job_description_id_job_descriptions", "ats_scores", type_="foreignkey")
    op.drop_constraint("fk_ats_scores_candidate_id_candidates", "ats_scores", type_="foreignkey")
    op.drop_column("ats_scores", "explanation")
    op.drop_column("ats_scores", "components")
    op.drop_column("ats_scores", "job_description_id")
    op.drop_column("ats_scores", "candidate_id")
