from abc import ABC, abstractmethod

class TranscriptionProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        ...

class TranscriptionService:
    def __init__(self, provider: TranscriptionProvider):
        self.provider = provider

    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        return await self.provider.transcribe(audio_bytes, mime_type)
