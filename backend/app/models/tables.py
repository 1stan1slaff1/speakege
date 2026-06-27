import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text, func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(320), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class QuestionRecord(Base):
    __tablename__ = "questions"

    id = Column(String(128), primary_key=True)
    task_type = Column(String(16), nullable=False, index=True)

    prompt_text = Column(Text, nullable=False)
    grading_prompt_text = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    image_urls = Column(JSON, nullable=False, default=list)
    image_captions = Column(JSON, nullable=False, default=list)
    reference_text = Column(Text, nullable=True)

    task2_prompts = Column(JSON, nullable=False, default=list)
    interviewer_intro = Column(Text, nullable=True)
    interview_questions = Column(JSON, nullable=False, default=list)
    audio = Column(JSON, nullable=True)

    prep_seconds = Column(Integer, nullable=False)
    record_seconds = Column(Integer, nullable=False)

    is_demo = Column(Boolean, nullable=False, default=False, index=True)
    is_curated = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    position = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Nullable until auth/guest tracking is implemented.
    user_id = Column(String(36), nullable=True, index=True)
    guest_id = Column(String(64), nullable=True, index=True)

    # question_id is nullable for legacy evaluate requests that still send prompt_text directly.
    question_id = Column(String(128), nullable=True, index=True)
    task_type = Column(String(16), nullable=False, index=True)

    status = Column(String(32), nullable=False, default="completed", index=True)
    source = Column(String(32), nullable=False, default="recorded")  # recorded | uploaded

    audio_url = Column(Text, nullable=True)
    audio_mime_type = Column(String(128), nullable=True)
    audio_size_bytes = Column(Integer, nullable=True)

    transcript = Column(Text, nullable=True)
    grade_json = Column(JSON, nullable=True)
    total_score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)

    credit_cost = Column(Integer, nullable=False, default=0)
    provider_meta_json = Column(JSON, nullable=True)

    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class CreditLedger(Base):
    __tablename__ = "credit_ledger"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)

    # Positive amount = credit grant, negative amount = credit deduction.
    amount = Column(Integer, nullable=False)
    reason = Column(String(64), nullable=False, index=True)

    attempt_id = Column(String(36), nullable=True, index=True)
    payment_id = Column(String(128), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ErrorTopic(Base):
    __tablename__ = "error_topics"

    id = Column(String(64), primary_key=True)
    title_ru = Column(String(255), nullable=False)
    short_explanation_ru = Column(Text, nullable=False)
    material_title = Column(String(255), nullable=True)
    material_url = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
