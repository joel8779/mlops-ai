"""complete recruiter auth and email workflow

Revision ID: 0009_recruiter_workflow_completion
Revises: 0008_add_otp_verification
Create Date: 2026-05-29
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0009_recruiter_workflow_completion"
down_revision: str | None = "0008_add_otp_verification"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.alter_column(
            "alembic_version",
            "version_num",
            existing_type=sa.String(32),
            type_=sa.String(128),
            existing_nullable=False,
        )

    op.drop_index("ix_organizations_organization_pin", table_name="organizations")
    op.alter_column("organizations", "organization_pin", type_=sa.String(255), existing_nullable=True)
    op.execute(
        "UPDATE users SET otp_verified = true "
        "WHERE otp_verified = false AND otp_code IS NULL AND otp_expiry IS NULL"
    )


def downgrade() -> None:
    op.alter_column("organizations", "organization_pin", type_=sa.String(6), existing_nullable=True)
    op.create_index("ix_organizations_organization_pin", "organizations", ["organization_pin"])
