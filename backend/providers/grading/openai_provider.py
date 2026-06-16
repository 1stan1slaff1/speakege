import json
import httpx
from app.services.grading import GradingProvider
from app.models.schemas import GradeResult, CriterionScore
from app.config import settings
from app.rubrics import get_rubric, get_max_total

class OpenAIGradingProvider(GradingProvider):
    API_URL = "https://api.openai.com/v1/chat/completions"

    async def grade(self, transcript: str, task_type: str, context: dict) -> GradeResult:
        rubric = get_rubric(task_type)
        official_max_total = get_max_total(task_type)

        system_prompt = f"""You are an expert ЕГЭ English examiner.
Grade the student response strictly according to the official-format rubric below.
The official maximum total for this task is {official_max_total}.

{rubric}

Return ONLY a JSON object in this exact format:
{{
    "criteria": {{
        "criterion_name": {{
            "score": <int>,
            "max_score": <int>,
            "feedback": "<specific feedback in Russian>"
        }}
    }},
    "total": <int>,
    "max_total": {official_max_total},
    "summary": "<overall feedback in Russian>"
}}

Rules:
- Do not exceed the official maximum score.
- Feedback must be in Russian.
- Be strict, but constructive.
- If the transcript is empty or unrelated to the task, award 0.
- Do not add criteria that are not part of the task rubric."""

        user_message = f"""Task type: {task_type}
Task prompt and context:
{context.get('prompt_text', '')}

Student response transcript:
{transcript}"""

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
            key: CriterionScore(
                score=max(0, min(int(value["score"]), int(value["max_score"]))),
                max_score=max(0, int(value["max_score"])),
                feedback=str(value["feedback"]),
            )
            for key, value in raw["criteria"].items()
        }

        if task_type == "task4" and criteria.get("content") and criteria["content"].score == 0:
            for key in ("organisation", "language"):
                if key in criteria:
                    criteria[key].score = 0

        calculated_total = sum(criterion.score for criterion in criteria.values())
        total = max(0, min(calculated_total, official_max_total))

        return GradeResult(
            criteria=criteria,
            total=total,
            max_total=official_max_total,
            summary=str(raw["summary"])
        )
