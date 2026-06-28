from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.feedback import list_active_error_topics
from app.models.schemas import ErrorTopicResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/error-topics", response_model=list[ErrorTopicResponse])
async def get_error_topics(
    task_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_active_error_topics(db, task_type=task_type)
