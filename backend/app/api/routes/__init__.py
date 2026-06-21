from fastapi import APIRouter
from app.api.routes import billing, evaluate, health, questions, submissions

router = APIRouter()
router.include_router(evaluate.router)
router.include_router(health.router)
router.include_router(billing.router)
router.include_router(questions.router)
router.include_router(submissions.router)
