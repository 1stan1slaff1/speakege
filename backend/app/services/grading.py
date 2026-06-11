from abc import ABC, abstractmethod
from app.models.schemas import GradeResult

class GradingProvider(ABC):
    @abstractmethod
    async def grade(self, transcript: str, task_type: str, context: dict) -> GradeResult:
        ...

class GradingService:
    def __init__(self, provider: GradingProvider):
        self.provider = provider

    async def grade(self, transcript: str, task_type: str, context: dict) -> GradeResult:
        return await self.provider.grade(transcript, task_type, context)
