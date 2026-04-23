"""announcements

Revision ID: 20260423_0005
Revises: 20260423_0004
Create Date: 2026-04-23
"""
from alembic import op
import sqlalchemy as sa

revision = "20260423_0005"
down_revision = "20260423_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "announcements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="published"),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_announcements_id", "announcements", ["id"])
    op.create_index("ix_announcements_workspace_id", "announcements", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_announcements_workspace_id", table_name="announcements")
    op.drop_index("ix_announcements_id", table_name="announcements")
    op.drop_table("announcements")
