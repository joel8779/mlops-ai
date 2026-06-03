"""add organization pin for access control

Revision ID: 0007_add_organization_pin
Revises: 0006_owner_isolation
Create Date: 2025-01-18
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0007_add_organization_pin"
down_revision: str | None = "0006_owner_isolation"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("organization_pin", sa.String(6), nullable=True))
    op.create_index("ix_organizations_organization_pin", "organizations", ["organization_pin"])


def downgrade() -> None:
    op.drop_index("ix_organizations_organization_pin", table_name="organizations")
    op.drop_column("organizations", "organization_pin")
