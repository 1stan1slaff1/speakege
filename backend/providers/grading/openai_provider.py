import json
import httpx
from app.services.grading import GradingProvider
from app.models.schemas import GradeResult, CriterionScore
from app.config import settings
from app.rubrics import get_rubric, get_max_total

TASK_FEEDBACK_GUIDELINES = {
    "task1": """
Task 1 feedback guidance:
- Explain the score in Russian in 2-4 short sentences.
- If pronunciation-assessment data is not provided, do not invent exact phonetic errors. Say that precise phonetic scoring requires audio-level assessment.
- Still comment on transcript-level evidence: completeness, omitted words/phrases, obvious substitutions, and whether the response looks like the given text.
- Give one practical pronunciation/reading tip.
""",
    "task2": """
Task 2 feedback guidance:
For each of question_1, question_2, question_3, question_4, feedback must be diagnostic and specific.
Use 2-4 short Russian sentences per question.
Do NOT write only "wrong word order" plus a correction if there are other important errors.

For each question, cover these points where relevant:
1. Content: say whether the required content point is covered (location, public transport, dentist, family discounts, etc.).
2. Direct-question form: say whether the grammar of a direct question is correct.
3. Error types: explicitly name all major errors that affect the score: missing auxiliary/linking verb, wrong word order, missing/incorrect article, wrong preposition, wrong lexical choice, content mismatch.
4. Correction: end with one corrected version.

Important distinctions:
- "Where the clinic located?" is missing the auxiliary/linking verb "is" after "where". Do not call this a missing article if "the" is present.
- "How I can get to the clinic...?" has wrong direct-question word order. Correct: "How can I get to the clinic...?"
- "Is there dentist at your clinic?" has correct inversion "Is there", but it is missing the article "a" before the singular countable noun "dentist".
- "Are there family discounts?" is generally acceptable if the content point is family discounts; "any" is more natural but should not be the only reason for 0.

Preferred feedback style example:
"Пункт про dentist раскрыт, но вопрос нельзя засчитать из-за грамматической ошибки. Конструкция 'Is there ...?' выбрана правильно, однако перед исчисляемым существительным в единственном числе нужен артикль: 'a dentist'. Правильный вариант: 'Is there a dentist at your clinic?'"
""",
    "task3": """
Task 3 feedback guidance:
- For each answer, say whether it answers the exact interviewer question.
- Mention if the answer is too short: one meaningful sentence or a fragment is not enough for 1 point.
- If the interviewer question has two parts, explicitly say whether both parts were answered.
- If the question asks why, explicitly say whether a reason was given.
- Name serious elementary grammar errors when they affect the score, and give a corrected example.
""",
    "task4": """
Task 4 feedback guidance:
- For content, name which of the four required aspects are complete, incomplete, inaccurate, or missing.
- For organisation, mention opening/address to friend, closing phrase, logical order, and linking devices.
- For language, name recurring grammar/vocabulary issues and give 1-2 corrected examples.
- If content is 0, clearly explain the zeroing rule in Russian: the whole task receives 0.
""",
}

class OpenAIGradingProvider(GradingProvider):
    API_URL = "https://api.openai.com/v1/chat/completions"

    async def grade(self, transcript: str, task_type: str, context: dict) -> GradeResult:
        rubric = get_rubric(task_type)
        official_max_total = get_max_total(task_type)
        feedback_guidelines = TASK_FEEDBACK_GUIDELINES.get(task_type, "")

        system_prompt = f"""You are an expert ЕГЭ English examiner.
Grade the student response strictly according to the official-format rubric below.
The official maximum total for this task is {official_max_total}.

{rubric}

{feedback_guidelines}

Return ONLY a JSON object in this exact format:
{{
    "criteria": {{
        "criterion_name": {{
            "score": <int>,
            "max_score": <int>,
            "feedback": "<specific diagnostic feedback in Russian>"
        }}
    }},
    "total": <int>,
    "max_total": {official_max_total},
    "summary": "<overall feedback in Russian>"
}}

General feedback quality rules:
- Feedback must be in Russian.
- Be strict, but constructive and educational.
- Explain WHY points were awarded or lost, not only WHAT the corrected answer is.
- If a response has multiple important problems, mention all major score-relevant problems. Do not give one-sided feedback.
- Quote the student's problematic fragment when it helps clarity.
- Provide a corrected version or corrected phrase for each non-perfect criterion when possible.
- Do not exceed the official maximum score.
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
