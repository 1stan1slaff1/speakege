#!/usr/bin/env python3
"""Seed current demo questions into the questions table.

Run from backend directory:
    python scripts/seed_demo_questions.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.questions.demo_bank import DEMO_QUESTIONS_BY_TASK_TYPE  # noqa: E402
from app.questions.store import upsert_question  # noqa: E402

TASK_ORDER = ["task1", "task2", "task3", "task4"]


def main() -> None:
    db = SessionLocal()
    try:
        for position, task_type in enumerate(TASK_ORDER, start=1):
            question = DEMO_QUESTIONS_BY_TASK_TYPE[task_type]
            record = upsert_question(db, question, is_demo=True, position=position)
            print(f"Seeded {record.id} ({record.task_type})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
