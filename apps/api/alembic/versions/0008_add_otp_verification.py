"""add otp email verification columns

Revision ID: 0008_add_otp_verification
Revises: 0007_add_organization_pin
Create Date: 2025-01-18
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0008_add_otp_verification"
down_revision: str | None = "0007_add_organization_pin"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("otp_code", sa.String(6), nullable=True))
    op.create_index("ix_users_otp_code", "users", ["otp_code"])
    op.add_column("users", sa.Column("otp_expiry", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("otp_verified", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("users", "otp_verified")
    op.drop_column("users", "otp_expiry")
    op.drop_index("ix_users_otp_code", table_name="users")
    op.drop_column("users", "otp_code")
