from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.database import get_db
from app.models.schemas import AttemptHistoryItem
from app.models.tables import User
from app.submissions import list_user_attempts

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.get("/history", response_model=list[AttemptHistoryItem])
async def get_attempt_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempts = list_user_attempts(db, user_id=current_user.id, limit=50)
    return [
        AttemptHistoryItem(
            id=attempt.id,
            question_id=attempt.question_id,
            task_type=attempt.task_type,
            status=attempt.status,
            source=attempt.source,
            total_score=attempt.total_score,
            max_score=attempt.max_score,
            credit_cost=attempt.credit_cost,
            created_at=attempt.created_at,
            completed_at=attempt.completed_at,
        )
        for attempt in attempts
    ]
