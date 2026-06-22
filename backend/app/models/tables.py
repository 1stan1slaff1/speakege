import uuid

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, func

from app.database import Base


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
