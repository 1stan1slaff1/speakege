"""add error topic metadata

Revision ID: 20260622_0006
Revises: 20260622_0005
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "20260622_0006"
down_revision = "20260622_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("error_topics", sa.Column("category", sa.String(length=32), nullable=False, server_default="language"))
    op.add_column("error_topics", sa.Column("applies_to_tasks", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
    op.add_column("error_topics", sa.Column("display_order", sa.Integer(), nullable=False, server_default="1000"))
    op.create_index("ix_error_topics_category", "error_topics", ["category"])


def downgrade() -> None:
    op.drop_index("ix_error_topics_category", table_name="error_topics")
    op.drop_column("error_topics", "display_order")
    op.drop_column("error_topics", "applies_to_tasks")
    op.drop_column("error_topics", "category")
