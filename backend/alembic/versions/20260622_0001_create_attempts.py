"""create attempts table

Revision ID: 20260622_0001
Revises: 
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "20260622_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("guest_id", sa.String(length=64), nullable=True),
        sa.Column("question_id", sa.String(length=128), nullable=True),
        sa.Column("task_type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("audio_url", sa.Text(), nullable=True),
        sa.Column("audio_mime_type", sa.String(length=128), nullable=True),
        sa.Column("audio_size_bytes", sa.Integer(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("grade_json", sa.JSON(), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=True),
        sa.Column("credit_cost", sa.Integer(), nullable=False),
        sa.Column("provider_meta_json", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])
    op.create_index("ix_attempts_guest_id", "attempts", ["guest_id"])
    op.create_index("ix_attempts_question_id", "attempts", ["question_id"])
    op.create_index("ix_attempts_task_type", "attempts", ["task_type"])
    op.create_index("ix_attempts_status", "attempts", ["status"])


def downgrade() -> None:
    op.drop_index("ix_attempts_status", table_name="attempts")
    op.drop_index("ix_attempts_task_type", table_name="attempts")
    op.drop_index("ix_attempts_question_id", table_name="attempts")
    op.drop_index("ix_attempts_guest_id", table_name="attempts")
    op.drop_index("ix_attempts_user_id", table_name="attempts")
    op.drop_table("attempts")
