import json
import httpx
from app.services.grading import GradingProvider
from app.models.schemas import GradeResult, CriterionScore
from app.config import settings
from app.rubrics import get_rubric

class OpenAIGradingProvider(GradingProvider):
    API_URL = "https://api.openai.com/v1/chat/completions"

    async def grade(self, transcript: str, task_type: str, context: dict) -> GradeResult:
        rubric = get_rubric(task_type)

        system_prompt = f"""You are an expert ЕГЭ English examiner. Grade the student response strictly according to this FIPI rubric:

{rubric}

Return ONLY a JSON object in this exact format:
{{
    "criteria": {{
        "criterion_name": {{
            "score": <int>,
            "max_score": <int>,
            "feedback": "<feedback in Russian>"
        }}
    }},
    "total": <int>,
    "max_total": <int>,
    "summary": "<overall feedback in Russian>"
}}"""

        user_message = f"Task type: {task_type}\nTask prompt: {context.get('prompt_text', '')}\nStudent response transcript:\n{transcript}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                },
                timeout=30.0
            )
            response.raise_for_status()
            raw = json.loads(response.json()["choices"][0]["message"]["content"])

        criteria = {
            k: CriterionScore(**v)
            for k, v in raw["criteria"].items()
        }

        return GradeResult(
            criteria=criteria,
            total=raw["total"],
            max_total=raw["max_total"],
            summary=raw["summary"]
        )
