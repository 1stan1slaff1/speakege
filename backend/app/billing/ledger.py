import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tables import CreditLedger


def add_credits(
    db: Session,
    *,
    user_id: str,
    amount: int,
    reason: str,
    attempt_id: str | None = None,
    payment_id: str | None = None,
) -> CreditLedger:
    entry = CreditLedger(
        id=str(uuid.uuid4()),
        user_id=user_id,
        amount=amount,
        reason=reason,
        attempt_id=attempt_id,
        payment_id=payment_id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_credit_balance(db: Session, *, user_id: str) -> int:
    balance = db.scalar(
        select(func.coalesce(func.sum(CreditLedger.amount), 0))
        .where(CreditLedger.user_id == user_id)
    )
    return int(balance or 0)
