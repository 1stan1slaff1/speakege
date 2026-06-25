from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import Question, QuestionListItem
from app.questions import (
    get_demo_question,
    get_demo_question_from_db,
    get_question_by_id,
    get_question_by_id_from_db,
    list_question_items_from_db,
)

router = APIRouter()


@router.get("/questions", response_model=list[QuestionListItem])
async def list_questions_route(
    task_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_question_items_from_db(db, task_type=task_type)


@router.get("/questions/demo/{task_type}", response_model=Question)
async def get_demo_question_route(task_type: str, db: Session = Depends(get_db)):
    # Prefer DB-backed questions. Fallback keeps local dev working before seeding.
    question = get_demo_question_from_db(db, task_type) or get_demo_question(task_type)
    if not question:
        raise HTTPException(status_code=404, detail="Demo question not found.")
    return question


@router.get("/questions/{question_id}", response_model=Question)
async def get_question_route(question_id: str, db: Session = Depends(get_db)):
    # Prefer DB-backed questions. Fallback keeps legacy demo ids working before seeding.
    question = get_question_by_id_from_db(db, question_id) or get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    return question
