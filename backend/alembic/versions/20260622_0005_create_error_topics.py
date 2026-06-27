"""create error topics table

Revision ID: 20260622_0005
Revises: 20260622_0004
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "20260622_0005"
down_revision = "20260622_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "error_topics",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("title_ru", sa.String(length=255), nullable=False),
        sa.Column("short_explanation_ru", sa.Text(), nullable=False),
        sa.Column("material_title", sa.String(length=255), nullable=True),
        sa.Column("material_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_error_topics_is_active", "error_topics", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_error_topics_is_active", table_name="error_topics")
    op.drop_table("error_topics")
