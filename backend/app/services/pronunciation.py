from abc import ABC, abstractmethod

class PronunciationProvider(ABC):
    @abstractmethod
    async def assess(self, audio_bytes: bytes, reference_text: str) -> dict:
        ...

class PronunciationService:
    def __init__(self, provider: PronunciationProvider | None = None):
        self.provider = provider

    async def assess(self, audio_bytes: bytes, reference_text: str) -> dict | None:
        if not self.provider:
            return None
        return await self.provider.assess(audio_bytes, reference_text)
