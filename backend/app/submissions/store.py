from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.schemas import GradeResult, SubmissionResponse
from app.models.tables import Attempt

PROVIDER_META = {
    "transcription": {
        "provider": "groq",
        "model": "whisper-large-v3",
    },
    "grading": {
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
    "pronunciation": {
        "provider": None,
        "model": None,
    },
}


def create_completed_attempt(
    db: Session,
    *,
    submission: SubmissionResponse,
    question_id: str | None,
    guest_id: str | None,
    source: str,
    audio_mime_type: str,
    audio_size_bytes: int,
    credit_cost: int,
) -> Attempt:
    now = datetime.now(timezone.utc)
    attempt = Attempt(
        id=submission.submission_id,
        question_id=question_id or None,
        guest_id=guest_id or None,
        task_type=submission.task_type,
        status="completed",
        source=source,
        audio_url=None,
        audio_mime_type=audio_mime_type,
        audio_size_bytes=audio_size_bytes,
        transcript=submission.transcript,
        grade_json=submission.grade.model_dump(),
        total_score=submission.grade.total,
        max_score=submission.grade.max_total,
        credit_cost=credit_cost,
        provider_meta_json=PROVIDER_META,
        started_at=now,
        completed_at=now,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_submission(db: Session, submission_id: str) -> SubmissionResponse | None:
    attempt = db.get(Attempt, submission_id)
    if not attempt or attempt.status != "completed" or not attempt.grade_json:
        return None

    return SubmissionResponse(
        submission_id=attempt.id,
        task_type=attempt.task_type,
        transcript=attempt.transcript or "",
        grade=GradeResult.model_validate(attempt.grade_json),
    )
