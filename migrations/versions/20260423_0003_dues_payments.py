"""dues payments

Revision ID: 20260423_0003
Revises: 20260423_0002
Create Date: 2026-04-23
"""
from alembic import op
import sqlalchemy as sa

revision = "20260423_0003"
down_revision = "20260423_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dues_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("cycle_id", sa.Integer(), sa.ForeignKey("dues_cycles.id"), nullable=False),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("workspace_members.id"), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("method", sa.String(length=30), nullable=False, server_default="manual"),
        sa.Column("gateway_ref", sa.String(length=160), nullable=True),
        sa.Column("receipt_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("confirmed_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_dues_payments_id", "dues_payments", ["id"])
    op.create_index("ix_dues_payments_workspace_id", "dues_payments", ["workspace_id"])
    op.create_index("ix_dues_payments_cycle_id", "dues_payments", ["cycle_id"])
    op.create_index("ix_dues_payments_member_id", "dues_payments", ["member_id"])
    op.create_index("ix_dues_payments_gateway_ref", "dues_payments", ["gateway_ref"], unique=True)
    op.create_index("ix_dues_payments_confirmed_by_user_id", "dues_payments", ["confirmed_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_dues_payments_confirmed_by_user_id", table_name="dues_payments")
    op.drop_index("ix_dues_payments_gateway_ref", table_name="dues_payments")
    op.drop_index("ix_dues_payments_member_id", table_name="dues_payments")
    op.drop_index("ix_dues_payments_cycle_id", table_name="dues_payments")
    op.drop_index("ix_dues_payments_workspace_id", table_name="dues_payments")
    op.drop_index("ix_dues_payments_id", table_name="dues_payments")
    op.drop_table("dues_payments")
