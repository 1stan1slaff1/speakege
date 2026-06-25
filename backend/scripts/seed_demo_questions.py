#!/usr/bin/env python3
"""Seed curated questions into the questions table.

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
from app.questions.demo_bank import get_question_seed_items  # noqa: E402
from app.questions.store import upsert_question  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        for question, is_demo, position in get_question_seed_items():
            record = upsert_question(db, question, is_demo=is_demo, position=position)
            label = "demo" if record.is_demo else "curated"
            print(f"Seeded {record.id} ({record.task_type}, {label}, position={record.position})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
