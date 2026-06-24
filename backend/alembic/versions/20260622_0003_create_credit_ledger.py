"""create credit ledger table

Revision ID: 20260622_0003
Revises: 20260622_0002
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "20260622_0003"
down_revision = "20260622_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "credit_ledger",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=False),
        sa.Column("attempt_id", sa.String(length=36), nullable=True),
        sa.Column("payment_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_credit_ledger_user_id", "credit_ledger", ["user_id"])
    op.create_index("ix_credit_ledger_reason", "credit_ledger", ["reason"])
    op.create_index("ix_credit_ledger_attempt_id", "credit_ledger", ["attempt_id"])
    op.create_index("ix_credit_ledger_payment_id", "credit_ledger", ["payment_id"])


def downgrade() -> None:
    op.drop_index("ix_credit_ledger_payment_id", table_name="credit_ledger")
    op.drop_index("ix_credit_ledger_attempt_id", table_name="credit_ledger")
    op.drop_index("ix_credit_ledger_reason", table_name="credit_ledger")
    op.drop_index("ix_credit_ledger_user_id", table_name="credit_ledger")
    op.drop_table("credit_ledger")
