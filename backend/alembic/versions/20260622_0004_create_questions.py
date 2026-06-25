"""create questions table

Revision ID: 20260622_0004
Revises: 20260622_0003
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "20260622_0004"
down_revision = "20260622_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("task_type", sa.String(length=16), nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("grading_prompt_text", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("image_urls", sa.JSON(), nullable=False),
        sa.Column("image_captions", sa.JSON(), nullable=False),
        sa.Column("reference_text", sa.Text(), nullable=True),
        sa.Column("task2_prompts", sa.JSON(), nullable=False),
        sa.Column("interviewer_intro", sa.Text(), nullable=True),
        sa.Column("interview_questions", sa.JSON(), nullable=False),
        sa.Column("audio", sa.JSON(), nullable=True),
        sa.Column("prep_seconds", sa.Integer(), nullable=False),
        sa.Column("record_seconds", sa.Integer(), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_curated", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_questions_task_type", "questions", ["task_type"])
    op.create_index("ix_questions_is_demo", "questions", ["is_demo"])
    op.create_index("ix_questions_is_active", "questions", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_questions_is_active", table_name="questions")
    op.drop_index("ix_questions_is_demo", table_name="questions")
    op.drop_index("ix_questions_task_type", table_name="questions")
    op.drop_table("questions")
