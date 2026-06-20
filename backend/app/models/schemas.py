from pydantic import BaseModel
from typing import Any

# Auth
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Questions
class Question(BaseModel):
    id: str
    task_type: str  # "task1" | "task2" | "task3" | "task4"
    prompt_text: str
    image_url: str | None = None
    reference_text: str | None = None  # Task 1 only — the text to read aloud
    prep_seconds: int
    record_seconds: int

# Grading
class CriterionScore(BaseModel):
    score: int
    max_score: int
    feedback: str

class GradeResult(BaseModel):
    criteria: dict[str, CriterionScore]
    total: int
    max_total: int
    summary: str


# Billing
class BillingPublicInfo(BaseModel):
    task_credit_cost: dict[str, int]
    free_registered_credits: int
    full_exam_credit_cost: int
    currency_label: str = "кредиты"

# Submissions
class SubmissionResponse(BaseModel):
    submission_id: str
    task_type: str
    transcript: str
    grade: GradeResult
