from app.models.schemas import SubmissionResponse

# Temporary in-memory submission store for MVP/local testing.
# This will be replaced by PostgreSQL-backed Attempt/Submission models later.
_SUBMISSIONS: dict[str, SubmissionResponse] = {}


def save_submission(submission: SubmissionResponse) -> None:
    _SUBMISSIONS[submission.submission_id] = submission


def get_submission(submission_id: str) -> SubmissionResponse | None:
    return _SUBMISSIONS.get(submission_id)
