import logging
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile
from sqlalchemy.orm import Session

from app.api.routes.auth import get_optional_current_user
from app.billing import add_credits, get_credit_balance, get_task_credit_cost
from app.database import get_db
from app.models.schemas import SubmissionResponse
from app.models.tables import User
from app.questions import get_question_by_id, get_question_by_id_from_db
from app.services.grading import GradingService
from app.services.guest import get_or_create_guest_id
from app.services.pronunciation import PronunciationService
from app.services.transcription import TranscriptionService
from app.submissions import count_completed_guest_attempts_for_task, create_completed_attempt
from providers.grading.openai_provider import OpenAIGradingProvider
from providers.transcription.groq_provider import GroqTranscriptionProvider

logger = logging.getLogger(__name__)
router = APIRouter()

GUEST_COMPLETED_ATTEMPTS_PER_TASK_LIMIT = 1

MAX_AUDIO_BYTES = 16 * 1024 * 1024
VALID_TASK_TYPES = {"task1", "task2", "task3", "task4"}
ALLOWED_AUDIO_CONTENT_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/aac",
    "audio/wav",
    "audio/x-wav",
}
AUDIO_CONTENT_TYPE_BY_EXTENSION = {
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".mp3": "audio/mpeg",
    ".mp4": "audio/mp4",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".wav": "audio/wav",
}
GENERIC_UPLOAD_CONTENT_TYPES = {"", "application/octet-stream"}

transcription = TranscriptionService(GroqTranscriptionProvider())
grading = GradingService(OpenAIGradingProvider())
pronunciation = PronunciationService()


def provider_status_message(provider_name: str, status_code: int) -> str:
    if status_code in {401, 403}:
        return f"{provider_name}: ошибка авторизации HTTP {status_code}. Проверьте API key и доступ к сервису."
    if status_code == 429:
        return f"{provider_name}: превышен лимит запросов или недостаточно quota/credits."
    if 500 <= status_code <= 599:
        return f"{provider_name}: временная ошибка сервиса HTTP {status_code}. Попробуйте позже."
    return f"{provider_name}: сервис вернул HTTP {status_code}. Проверьте backend-логи."


def refund_credits_if_needed(
    db: Session,
    *,
    user: User | None,
    credits_deducted: bool,
    credit_cost: int,
    attempt_id: str,
) -> None:
    if not user or not credits_deducted or credit_cost <= 0:
        return

    add_credits(
        db,
        user_id=user.id,
        amount=credit_cost,
        reason="refund_failed_evaluation",
        attempt_id=attempt_id,
    )


def normalize_audio_content_type(audio: UploadFile) -> str:
    raw_content_type = (audio.content_type or "").split(";")[0].strip().lower()

    if raw_content_type in ALLOWED_AUDIO_CONTENT_TYPES:
        # Groq/OpenAI-style APIs usually understand audio/mp4 better than audio/m4a.
        if raw_content_type in {"audio/m4a", "audio/x-m4a"}:
            return "audio/mp4"
        return raw_content_type

    if raw_content_type not in GENERIC_UPLOAD_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported audio format.")

    suffix = Path(audio.filename or "").suffix.lower()
    inferred_content_type = AUDIO_CONTENT_TYPE_BY_EXTENSION.get(suffix)

    if not inferred_content_type:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format. Use mp3, wav, m4a/mp4, webm, ogg or aac.",
        )

    return inferred_content_type


def resolve_task_and_prompt(db: Session, task_type: str, question_id: str, prompt_text: str) -> tuple[str, str]:
    if question_id:
        # Prefer DB-backed questions. Fallback keeps legacy demo ids working before seeding.
        question = get_question_by_id_from_db(db, question_id) or get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found.")
        return question.task_type, (question.grading_prompt_text or question.prompt_text)[:8000]

    if task_type not in VALID_TASK_TYPES:
        raise HTTPException(status_code=400, detail="Invalid task type.")

    return task_type, prompt_text[:8000]


@router.post("/evaluate", response_model=SubmissionResponse)
async def evaluate(
    request: Request,
    response: Response,
    audio: UploadFile = File(...),
    task_type: str = Form(default=""),
    prompt_text: str = Form(default=""),
    question_id: str = Form(default=""),
    source: str = Form(default="recorded"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    resolved_task_type, resolved_prompt_text = resolve_task_and_prompt(db, task_type, question_id, prompt_text)
    credit_cost = get_task_credit_cost(resolved_task_type)
    normalized_source = source if source in {"recorded", "uploaded"} else "recorded"
    guest_id = None if current_user else get_or_create_guest_id(request, response)

    if not current_user and guest_id:
        completed_attempts_for_task = count_completed_guest_attempts_for_task(
            db,
            guest_id=guest_id,
            task_type=resolved_task_type,
        )
        if completed_attempts_for_task >= GUEST_COMPLETED_ATTEMPTS_PER_TASK_LIMIT:
            raise HTTPException(
                status_code=403,
                detail="Вы уже использовали бесплатную AI-проверку для этого типа задания. Зарегистрируйтесь, чтобы получить стартовый баланс кредитов и доступ к большему числу проверок.",
            )

    content_type = normalize_audio_content_type(audio)

    audio_bytes = await audio.read(MAX_AUDIO_BYTES + 1)

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio file is empty.")

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail="Audio file too large. Maximum size is 16MB.")

    submission_id = str(uuid.uuid4())
    credits_deducted = False

    if current_user:
        credit_balance = get_credit_balance(db, user_id=current_user.id)
        if credit_balance < credit_cost:
            raise HTTPException(
                status_code=402,
                detail=f"Недостаточно кредитов для AI-проверки. Нужно: {credit_cost}, доступно: {credit_balance}.",
            )

        add_credits(
            db,
            user_id=current_user.id,
            amount=-credit_cost,
            reason="task_evaluation",
            attempt_id=submission_id,
        )
        credits_deducted = True

    try:
        transcript = await transcription.transcribe(audio_bytes, content_type)
    except httpx.HTTPStatusError as exc:
        refund_credits_if_needed(
            db,
            user=current_user,
            credits_deducted=credits_deducted,
            credit_cost=credit_cost,
            attempt_id=submission_id,
        )
        logger.exception("Groq transcription returned an HTTP error: %s", exc.response.text)
        raise HTTPException(
            status_code=502,
            detail=provider_status_message("Groq transcription", exc.response.status_code),
        ) from exc
    except httpx.RequestError as exc:
        refund_credits_if_needed(
            db,
            user=current_user,
            credits_deducted=credits_deducted,
            credit_cost=credit_cost,
            attempt_id=submission_id,
        )
        logger.exception("Could not connect to Groq transcription")
        raise HTTPException(
            status_code=502,
            detail="Не удалось подключиться к Groq для транскрибации. Если backend запущен локально в РФ, проверьте системный VPN/proxy или доступность api.groq.com.",
        ) from exc
    except Exception as exc:
        refund_credits_if_needed(
            db,
            user=current_user,
            credits_deducted=credits_deducted,
            credit_cost=credit_cost,
            attempt_id=submission_id,
        )
        logger.exception("Unexpected transcription error")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при транскрибации. Подробности смотрите в терминале backend.",
        ) from exc

    context = {"prompt_text": resolved_prompt_text}

    try:
        grade_result = await grading.grade(
            transcript=transcript,
            task_type=resolved_task_type,
            context=context
        )
    except httpx.HTTPStatusError as exc:
        refund_credits_if_needed(
            db,
            user=current_user,
            credits_deducted=credits_deducted,
            credit_cost=credit_cost,
            attempt_id=submission_id,
        )
        logger.exception("OpenAI grading returned an HTTP error: %s", exc.response.text)
        raise HTTPException(
            status_code=502,
            detail=provider_status_message("OpenAI grading", exc.response.status_code),
        ) from exc
    except httpx.RequestError as exc:
        refund_credits_if_needed(
            db,
            user=current_user,
            credits_deducted=credits_deducted,
            credit_cost=credit_cost,
            attempt_id=submission_id,
        )
        logger.exception("Could not connect to OpenAI grading")
        raise HTTPException(
            status_code=502,
            detail="Не удалось подключиться к OpenAI для проверки ответа. Если backend запущен локально в РФ, проверьте системный VPN/proxy или доступность api.openai.com.",
        ) from exc
    except Exception as exc:
        refund_credits_if_needed(
            db,
            user=current_user,
            credits_deducted=credits_deducted,
            credit_cost=credit_cost,
            attempt_id=submission_id,
        )
        logger.exception("Unexpected grading error")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при проверке ответа. Подробности смотрите в терминале backend.",
        ) from exc

    submission = SubmissionResponse(
        submission_id=submission_id,
        task_type=resolved_task_type,
        transcript=transcript,
        grade=grade_result
    )
    create_completed_attempt(
        db,
        submission=submission,
        question_id=question_id or None,
        user_id=current_user.id if current_user else None,
        guest_id=guest_id,
        source=normalized_source,
        audio_mime_type=content_type,
        audio_size_bytes=len(audio_bytes),
        credit_cost=credit_cost,
    )
    return submission
