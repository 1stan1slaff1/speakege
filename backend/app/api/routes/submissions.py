from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import SubmissionResponse
from app.submissions import get_submission

router = APIRouter()


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission_route(submission_id: str, db: Session = Depends(get_db)):
    submission = get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission
