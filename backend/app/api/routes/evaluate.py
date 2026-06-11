from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.transcription import TranscriptionService
from app.services.grading import GradingService
from app.services.pronunciation import PronunciationService
from app.models.schemas import SubmissionResponse, GradeResult, CriterionScore
from providers.transcription.groq_provider import GroqTranscriptionProvider
from providers.grading.openai_provider import OpenAIGradingProvider
import uuid

router = APIRouter()

transcription = TranscriptionService(GroqTranscriptionProvider())
grading = GradingService(OpenAIGradingProvider())
pronunciation = PronunciationService()

@router.post("/evaluate", response_model=SubmissionResponse)
async def evaluate(
    audio: UploadFile = File(...),
    task_type: str = Form(...),
    prompt_text: str = Form(default="")
):
    if audio.size and audio.size > 16 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Audio file too large. Maximum size is 16MB.")

    if task_type not in ["task1", "task2", "task3", "task4"]:
        raise HTTPException(status_code=400, detail="Invalid task type.")

    audio_bytes = await audio.read()

    transcript = await transcription.transcribe(audio_bytes, audio.content_type or "audio/webm")

    context = {"prompt_text": prompt_text}

    grade_result = await grading.grade(
        transcript=transcript,
        task_type=task_type,
        context=context
    )

    return SubmissionResponse(
        submission_id=str(uuid.uuid4()),
        transcript=transcript,
        grade=grade_result
    )
