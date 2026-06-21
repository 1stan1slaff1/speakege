from fastapi import APIRouter, HTTPException

from app.models.schemas import Question
from app.questions import get_demo_question, get_question_by_id

router = APIRouter()


@router.get("/questions/demo/{task_type}", response_model=Question)
async def get_demo_question_route(task_type: str):
    question = get_demo_question(task_type)
    if not question:
        raise HTTPException(status_code=404, detail="Demo question not found.")
    return question


@router.get("/questions/{question_id}", response_model=Question)
async def get_question_route(question_id: str):
    question = get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    return question
