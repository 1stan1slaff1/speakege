from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.feedback import list_active_error_topics
from app.models.schemas import ErrorTopicResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/error-topics", response_model=list[ErrorTopicResponse])
async def get_error_topics(db: Session = Depends(get_db)):
    return list_active_error_topics(db)
