"""campaign contributions

Revision ID: 20260423_0004
Revises: 20260423_0003
Create Date: 2026-04-23
"""
from alembic import op
import sqlalchemy as sa

revision = "20260423_0004"
down_revision = "20260423_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "funding_streams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("stream_type", sa.String(length=40), nullable=False, server_default="general"),
        sa.Column("target_amount", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_funding_streams_id", "funding_streams", ["id"])
    op.create_index("ix_funding_streams_workspace_id", "funding_streams", ["workspace_id"])
    op.create_index("ix_funding_streams_campaign_id", "funding_streams", ["campaign_id"])

    op.create_table(
        "contributions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("stream_id", sa.Integer(), sa.ForeignKey("funding_streams.id"), nullable=True),
        sa.Column("contributor_name", sa.String(length=160), nullable=True),
        sa.Column("contributor_email", sa.String(length=180), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("method", sa.String(length=30), nullable=False, server_default="public"),
        sa.Column("gateway_ref", sa.String(length=160), nullable=True),
        sa.Column("receipt_url", sa.String(length=500), nullable=True),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("confirmed_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_contributions_id", "contributions", ["id"])
    op.create_index("ix_contributions_workspace_id", "contributions", ["workspace_id"])
    op.create_index("ix_contributions_campaign_id", "contributions", ["campaign_id"])
    op.create_index("ix_contributions_stream_id", "contributions", ["stream_id"])
    op.create_index("ix_contributions_gateway_ref", "contributions", ["gateway_ref"], unique=True)
    op.create_index("ix_contributions_confirmed_by_user_id", "contributions", ["confirmed_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_contributions_confirmed_by_user_id", table_name="contributions")
    op.drop_index("ix_contributions_gateway_ref", table_name="contributions")
    op.drop_index("ix_contributions_stream_id", table_name="contributions")
    op.drop_index("ix_contributions_campaign_id", table_name="contributions")
    op.drop_index("ix_contributions_workspace_id", table_name="contributions")
    op.drop_index("ix_contributions_id", table_name="contributions")
    op.drop_table("contributions")

    op.drop_index("ix_funding_streams_campaign_id", table_name="funding_streams")
    op.drop_index("ix_funding_streams_workspace_id", table_name="funding_streams")
    op.drop_index("ix_funding_streams_id", table_name="funding_streams")
    op.drop_table("funding_streams")
