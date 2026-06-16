import logging
import uuid

import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.transcription import TranscriptionService
from app.services.grading import GradingService
from app.services.pronunciation import PronunciationService
from app.models.schemas import SubmissionResponse
from providers.transcription.groq_provider import GroqTranscriptionProvider
from providers.grading.openai_provider import OpenAIGradingProvider

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_AUDIO_BYTES = 16 * 1024 * 1024
ALLOWED_AUDIO_CONTENT_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
}

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


@router.post("/evaluate", response_model=SubmissionResponse)
async def evaluate(
    audio: UploadFile = File(...),
    task_type: str = Form(...),
    prompt_text: str = Form(default="")
):
    if task_type not in ["task1", "task2", "task3", "task4"]:
        raise HTTPException(status_code=400, detail="Invalid task type.")

    content_type = (audio.content_type or "").split(";")[0].strip().lower()
    if content_type and content_type not in ALLOWED_AUDIO_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported audio format.")

    audio_bytes = await audio.read(MAX_AUDIO_BYTES + 1)

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio file is empty.")

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail="Audio file too large. Maximum size is 16MB.")

    try:
        transcript = await transcription.transcribe(audio_bytes, content_type or "audio/webm")
    except httpx.HTTPStatusError as exc:
        logger.exception("Groq transcription returned an HTTP error: %s", exc.response.text)
        raise HTTPException(
            status_code=502,
            detail=provider_status_message("Groq transcription", exc.response.status_code),
        ) from exc
    except httpx.RequestError as exc:
        logger.exception("Could not connect to Groq transcription")
        raise HTTPException(
            status_code=502,
            detail="Не удалось подключиться к Groq для транскрибации. Если backend запущен локально в РФ, проверьте системный VPN/proxy или доступность api.groq.com.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected transcription error")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при транскрибации. Подробности смотрите в терминале backend.",
        ) from exc

    context = {"prompt_text": prompt_text[:8000]}

    try:
        grade_result = await grading.grade(
            transcript=transcript,
            task_type=task_type,
            context=context
        )
    except httpx.HTTPStatusError as exc:
        logger.exception("OpenAI grading returned an HTTP error: %s", exc.response.text)
        raise HTTPException(
            status_code=502,
            detail=provider_status_message("OpenAI grading", exc.response.status_code),
        ) from exc
    except httpx.RequestError as exc:
        logger.exception("Could not connect to OpenAI grading")
        raise HTTPException(
            status_code=502,
            detail="Не удалось подключиться к OpenAI для проверки ответа. Если backend запущен локально в РФ, проверьте системный VPN/proxy или доступность api.openai.com.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected grading error")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при проверке ответа. Подробности смотрите в терминале backend.",
        ) from exc

    return SubmissionResponse(
        submission_id=str(uuid.uuid4()),
        task_type=task_type,
        transcript=transcript,
        grade=grade_result
    )
