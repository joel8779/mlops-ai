"""align pipeline stages with recruiter workflow contract

Revision ID: 0005_pipeline_stage_contract
Revises: 0004_job_context_ats
Create Date: 2026-05-25
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0005_pipeline_stage_contract"
down_revision: str | None = "0004_job_context_ats"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE pipelinestage RENAME TO pipelinestage_old")
    op.execute("CREATE TYPE pipelinestage AS ENUM ('uploaded', 'ranked', 'shortlisted', 'interviewing', 'rejected', 'hired')")
    op.execute(
        """
        ALTER TABLE candidate_pipeline_stages
        ALTER COLUMN stage TYPE pipelinestage
        USING (
            CASE stage::text
                WHEN 'Applied' THEN 'uploaded'
                WHEN 'Screening' THEN 'ranked'
                WHEN 'Interview' THEN 'interviewing'
                WHEN 'Technical Round' THEN 'interviewing'
                WHEN 'Final Round' THEN 'interviewing'
                WHEN 'Hired' THEN 'hired'
                WHEN 'Rejected' THEN 'rejected'
                ELSE 'uploaded'
            END
        )::pipelinestage
        """
    )
    op.execute("DROP TYPE pipelinestage_old")


def downgrade() -> None:
    op.execute("ALTER TYPE pipelinestage RENAME TO pipelinestage_old")
    op.execute(
        "CREATE TYPE pipelinestage AS ENUM ('Applied', 'Screening', 'Interview', 'Technical Round', 'Final Round', 'Hired', 'Rejected')"
    )
    op.execute(
        """
        ALTER TABLE candidate_pipeline_stages
        ALTER COLUMN stage TYPE pipelinestage
        USING (
            CASE stage::text
                WHEN 'uploaded' THEN 'Applied'
                WHEN 'ranked' THEN 'Screening'
                WHEN 'shortlisted' THEN 'Screening'
                WHEN 'interviewing' THEN 'Interview'
                WHEN 'hired' THEN 'Hired'
                WHEN 'rejected' THEN 'Rejected'
                ELSE 'Applied'
            END
        )::pipelinestage
        """
    )
    op.execute("DROP TYPE pipelinestage_old")
