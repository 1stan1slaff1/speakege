from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.schemas import Question, QuestionAudio, QuestionListItem
from app.models.tables import QuestionRecord


def question_record_to_schema(record: QuestionRecord) -> Question:
    return Question(
        id=record.id,
        task_type=record.task_type,
        prompt_text=record.prompt_text,
        grading_prompt_text=record.grading_prompt_text,
        image_url=record.image_url,
        image_urls=record.image_urls or [],
        image_captions=record.image_captions or [],
        reference_text=record.reference_text,
        task2_prompts=record.task2_prompts or [],
        interviewer_intro=record.interviewer_intro,
        interview_questions=record.interview_questions or [],
        audio=QuestionAudio.model_validate(record.audio) if record.audio else None,
        prep_seconds=record.prep_seconds,
        record_seconds=record.record_seconds,
    )


def question_record_to_list_item(record: QuestionRecord) -> QuestionListItem:
    title = record.prompt_text.splitlines()[0].replace("Task 1. ", "").replace("Task 2. ", "").replace("Task 3. ", "").replace("Task 4. ", "")
    if len(title) > 90:
        title = title[:87].rstrip() + "..."

    return QuestionListItem(
        id=record.id,
        task_type=record.task_type,
        title=title,
        is_demo=record.is_demo,
        is_curated=record.is_curated,
        position=record.position,
        prep_seconds=record.prep_seconds,
        record_seconds=record.record_seconds,
    )


def question_schema_to_record(question: Question, *, is_demo: bool, position: int) -> QuestionRecord:
    return QuestionRecord(
        id=question.id,
        task_type=question.task_type,
        prompt_text=question.prompt_text,
        grading_prompt_text=question.grading_prompt_text,
        image_url=question.image_url,
        image_urls=question.image_urls,
        image_captions=question.image_captions,
        reference_text=question.reference_text,
        task2_prompts=question.task2_prompts,
        interviewer_intro=question.interviewer_intro,
        interview_questions=question.interview_questions,
        audio=question.audio.model_dump() if question.audio else None,
        prep_seconds=question.prep_seconds,
        record_seconds=question.record_seconds,
        is_demo=is_demo,
        is_curated=True,
        is_active=True,
        position=position,
    )


def list_question_items_from_db(
    db: Session,
    *,
    task_type: str | None = None,
    include_inactive: bool = False,
    limit: int = 100,
) -> list[QuestionListItem]:
    statement = select(QuestionRecord)
    if task_type:
        statement = statement.where(QuestionRecord.task_type == task_type)
    if not include_inactive:
        statement = statement.where(QuestionRecord.is_active.is_(True))

    statement = statement.order_by(
        QuestionRecord.task_type.asc(),
        QuestionRecord.position.asc(),
        QuestionRecord.created_at.asc(),
    ).limit(limit)

    return [question_record_to_list_item(record) for record in db.scalars(statement)]


def list_questions_from_db(
    db: Session,
    *,
    task_type: str | None = None,
    include_inactive: bool = False,
    limit: int = 100,
) -> list[Question]:
    statement = select(QuestionRecord)
    if task_type:
        statement = statement.where(QuestionRecord.task_type == task_type)
    if not include_inactive:
        statement = statement.where(QuestionRecord.is_active.is_(True))

    statement = statement.order_by(
        QuestionRecord.task_type.asc(),
        QuestionRecord.position.asc(),
        QuestionRecord.created_at.asc(),
    ).limit(limit)

    return [question_record_to_schema(record) for record in db.scalars(statement)]


def is_demo_question_in_db(db: Session, question_id: str) -> bool | None:
    record = db.get(QuestionRecord, question_id)
    if not record:
        return None
    return bool(record.is_demo)


def get_question_by_id_from_db(db: Session, question_id: str) -> Question | None:
    record = db.get(QuestionRecord, question_id)
    if not record or not record.is_active:
        return None
    return question_record_to_schema(record)


def get_demo_question_from_db(db: Session, task_type: str) -> Question | None:
    record = db.scalar(
        select(QuestionRecord)
        .where(
            QuestionRecord.task_type == task_type,
            QuestionRecord.is_demo.is_(True),
            QuestionRecord.is_active.is_(True),
        )
        .order_by(QuestionRecord.position.asc(), QuestionRecord.created_at.asc())
        .limit(1)
    )
    return question_record_to_schema(record) if record else None


def upsert_question(db: Session, question: Question, *, is_demo: bool, position: int) -> QuestionRecord:
    existing = db.get(QuestionRecord, question.id)
    replacement = question_schema_to_record(question, is_demo=is_demo, position=position)

    if existing:
        existing.task_type = replacement.task_type
        existing.prompt_text = replacement.prompt_text
        existing.grading_prompt_text = replacement.grading_prompt_text
        existing.image_url = replacement.image_url
        existing.image_urls = replacement.image_urls
        existing.image_captions = replacement.image_captions
        existing.reference_text = replacement.reference_text
        existing.task2_prompts = replacement.task2_prompts
        existing.interviewer_intro = replacement.interviewer_intro
        existing.interview_questions = replacement.interview_questions
        existing.audio = replacement.audio
        existing.prep_seconds = replacement.prep_seconds
        existing.record_seconds = replacement.record_seconds
        existing.is_demo = replacement.is_demo
        existing.is_curated = replacement.is_curated
        existing.is_active = replacement.is_active
        existing.position = replacement.position
        record = existing
    else:
        db.add(replacement)
        record = replacement

    db.commit()
    db.refresh(record)
    return record
