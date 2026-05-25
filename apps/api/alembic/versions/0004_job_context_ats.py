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
    op.add_column("ats_scores", sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("ats_scores", sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("ats_scores", sa.Column("components", postgresql.JSONB(), nullable=False, server_default="[]"))
    op.add_column("ats_scores", sa.Column("explanation", sa.Text(), nullable=True))
    op.create_foreign_key("fk_ats_scores_candidate_id_candidates", "ats_scores", "candidates", ["candidate_id"], ["id"])
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
        UPDATE ats_scores
        SET job_description_id = candidate_matches.job_description_id,
            ats_score = candidate_matches.overall_score,
            explanation = candidate_matches.explanation,
            scoring_version = 'ats-job-context-v1'
        FROM candidate_matches
        WHERE ats_scores.candidate_id = candidate_matches.candidate_id
          AND ats_scores.job_description_id IS NULL
        """
    )
    op.execute("DELETE FROM ats_scores WHERE candidate_id IS NULL OR job_description_id IS NULL")
    op.alter_column("ats_scores", "candidate_id", nullable=False)
    op.alter_column("ats_scores", "job_description_id", nullable=False)
    op.create_unique_constraint("uq_ats_score_candidate_job", "ats_scores", ["candidate_id", "job_description_id"])
    op.create_index("ix_ats_scores_job_score", "ats_scores", ["job_description_id", "ats_score"])


def downgrade() -> None:
    op.drop_index("ix_ats_scores_job_score", table_name="ats_scores")
    op.drop_constraint("uq_ats_score_candidate_job", "ats_scores", type_="unique")
    op.drop_constraint("fk_ats_scores_job_description_id_job_descriptions", "ats_scores", type_="foreignkey")
    op.drop_constraint("fk_ats_scores_candidate_id_candidates", "ats_scores", type_="foreignkey")
    op.drop_column("ats_scores", "explanation")
    op.drop_column("ats_scores", "components")
    op.drop_column("ats_scores", "job_description_id")
    op.drop_column("ats_scores", "candidate_id")
