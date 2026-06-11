import httpx
from app.services.transcription import TranscriptionProvider
from app.config import settings

class GroqTranscriptionProvider(TranscriptionProvider):
    API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.API_URL,
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                files={"file": ("audio.webm", audio_bytes, mime_type)},
                data={"model": "whisper-large-v3", "language": "en"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["text"]
