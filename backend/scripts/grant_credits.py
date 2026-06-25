#!/usr/bin/env python3
"""Grant credits to a user by email.

Run from backend directory:
    python scripts/grant_credits.py user@example.com 100 manual_test_grant

Positive amounts add credits. This script intentionally rejects zero/negative
amounts; use a separate admin adjustment script later if deductions are needed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running both from repository root and from backend/.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select  # noqa: E402

from app.billing import add_credits, get_credit_balance  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models.tables import User  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grant credits to a SpeakEGE user.")
    parser.add_argument("email", help="User email, e.g. student@example.com")
    parser.add_argument("amount", type=int, help="Positive number of credits to grant")
    parser.add_argument(
        "reason",
        nargs="?",
        default="manual_grant",
        help="Ledger reason, default: manual_grant",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    email = args.email.strip().lower()

    if args.amount <= 0:
        raise SystemExit("Amount must be a positive integer.")

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            raise SystemExit(f"User not found: {email}")

        before = get_credit_balance(db, user_id=user.id)
        entry = add_credits(
            db,
            user_id=user.id,
            amount=args.amount,
            reason=args.reason,
        )
        after = get_credit_balance(db, user_id=user.id)

        print(f"User:      {user.email}")
        print(f"User ID:   {user.id}")
        print(f"Ledger ID: {entry.id}")
        print(f"Reason:    {args.reason}")
        print(f"Granted:   +{args.amount}")
        print(f"Balance:   {before} -> {after}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
