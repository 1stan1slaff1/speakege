from fastapi import APIRouter, HTTPException

from app.models.schemas import SubmissionResponse
from app.submissions import get_submission

router = APIRouter()


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission_route(submission_id: str):
    submission = get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission
