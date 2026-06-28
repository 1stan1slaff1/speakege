from datetime import datetime

from pydantic import BaseModel, Field

# Auth
class UserRegister(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
    credit_balance: int = 0

# Questions
class QuestionAudio(BaseModel):
    intro: str | None = None
    start_cue: str | None = None
    question_cues: list[str] = Field(default_factory=list)
    end: str | None = None

class Question(BaseModel):
    id: str
    task_type: str  # "task1" | "task2" | "task3" | "task4"
    prompt_text: str
    grading_prompt_text: str | None = None
    image_url: str | None = None
    image_urls: list[str] = Field(default_factory=list)
    image_captions: list[str] = Field(default_factory=list)
    reference_text: str | None = None  # Task 1 only — the text to read aloud
    task2_prompts: list[str] = Field(default_factory=list)
    interviewer_intro: str | None = None
    interview_questions: list[str] = Field(default_factory=list)
    audio: QuestionAudio | None = None
    prep_seconds: int
    record_seconds: int


class QuestionListItem(BaseModel):
    id: str
    task_type: str
    title: str
    is_demo: bool
    is_curated: bool
    position: int
    prep_seconds: int
    record_seconds: int

# Grading
class FeedbackIssue(BaseModel):
    topic_id: str
    fragment: str | None = None
    correction: str | None = None
    explanation_ru: str

class CriterionScore(BaseModel):
    score: int
    max_score: int
    feedback: str
    issues: list[FeedbackIssue] = Field(default_factory=list)

class ErrorTopicResponse(BaseModel):
    id: str
    title_ru: str
    short_explanation_ru: str
    material_title: str | None = None
    material_url: str | None = None
    category: str = "language"
    applies_to_tasks: list[str] = Field(default_factory=list)
    display_order: int = 1000

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

# Attempts
class AttemptHistoryItem(BaseModel):
    id: str
    question_id: str | None = None
    task_type: str
    status: str
    source: str
    total_score: int | None = None
    max_score: int | None = None
    credit_cost: int
    created_at: datetime
    completed_at: datetime | None = None

# Submissions
class SubmissionResponse(BaseModel):
    submission_id: str
    task_type: str
    transcript: str
    grade: GradeResult
