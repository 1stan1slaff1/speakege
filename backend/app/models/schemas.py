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

# Submissions
class SubmissionResponse(BaseModel):
    submission_id: str
    task_type: str
    transcript: str
    grade: GradeResult
