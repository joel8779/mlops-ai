"""add composite index for candidate pipeline stages

Revision ID: 0010_composite_indexes
Revises: 0009_recruiter_workflow_completion
Create Date: 2026-06-03
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0010_composite_indexes"
down_revision: str | None = "0009_recruiter_workflow_completion"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_index(
        "ix_candidate_pipeline_stages_org_del_stage",
        "candidate_pipeline_stages",
        ["organization_id", "deleted_at", "stage"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_candidate_pipeline_stages_org_del_stage",
        table_name="candidate_pipeline_stages",
    )
