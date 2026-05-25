"""enterprise scale primitives

Revision ID: 0003_enterprise_scale
Revises: 0002_ai_intelligence_workflow
Create Date: 2026-05-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_enterprise_scale"
down_revision: str | None = "0002_ai_intelligence_workflow"
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
    feedback_action = postgresql.ENUM(
        "shortlist", "reject", "interview", "hire", name="feedbackaction", create_type=False
    )
    subscription_tier = postgresql.ENUM(
        "free", "growth", "enterprise", name="subscriptiontier", create_type=False
    )
    feedback_action.create(op.get_bind(), checkfirst=True)
    subscription_tier.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "ranking_feedback",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", feedback_action, nullable=False),
        sa.Column("reward", sa.Numeric(5, 2), nullable=False),
        sa.Column("rank_position", sa.Integer(), nullable=True),
        sa.Column("model_version", sa.String(120), nullable=True),
        sa.Column("feature_snapshot", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["job_description_id"], ["job_descriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ranking_feedback_action", "ranking_feedback", ["action"])
    op.create_index("ix_ranking_feedback_reward", "ranking_feedback", ["reward"])

    op.create_table(
        "audit_logs",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("resource_type", sa.String(120), nullable=False),
        sa.Column("resource_id", sa.String(120), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])

    op.create_table(
        "api_keys",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("scopes", postgresql.JSONB(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])

    op.create_table(
        "tenant_quotas",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tier", subscription_tier, nullable=False),
        sa.Column("monthly_resume_limit", sa.Integer(), nullable=False),
        sa.Column("monthly_llm_token_limit", sa.Integer(), nullable=False),
        sa.Column("monthly_vector_query_limit", sa.Integer(), nullable=False),
        sa.Column("usage_counters", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
    )

    op.create_table(
        "recruiter_conversations",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("memory", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "recruiter_messages",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["conversation_id"], ["recruiter_conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "analytics_snapshots",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_type", sa.String(100), nullable=False),
        sa.Column("metrics", postgresql.JSONB(), nullable=False),
        *base_columns(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_snapshots_snapshot_type", "analytics_snapshots", ["snapshot_type"])


def downgrade() -> None:
    for table in [
        "analytics_snapshots",
        "recruiter_messages",
        "recruiter_conversations",
        "tenant_quotas",
        "api_keys",
        "audit_logs",
        "ranking_feedback",
    ]:
        op.drop_table(table)
    postgresql.ENUM(name="subscriptiontier").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="feedbackaction").drop(op.get_bind(), checkfirst=True)
