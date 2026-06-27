#!/usr/bin/env python3
"""Seed supported feedback/error topics into the database.

Run from backend directory:
    python scripts/seed_error_topics.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.feedback import ERROR_TOPIC_SEED_DATA, upsert_error_topic  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        for item in ERROR_TOPIC_SEED_DATA:
            topic = upsert_error_topic(db, item)
            print(f"Seeded {topic.id}: {topic.title_ru}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
