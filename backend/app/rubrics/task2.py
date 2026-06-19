TASK2_RUBRIC = """
ЕГЭ English Speaking — Task 2 / Задание 2: Asking direct questions based on an advertisement
Official maximum score: 4 points: 1 point for each of 4 direct questions.

The student must ask FOUR direct questions matching the four content prompts in the task. Each question is evaluated independently. Return criteria with keys "question_1", "question_2", "question_3", "question_4".

For each question — max 1 point:
- 1 point: The question matches the required content point; it has the correct grammatical form of a direct question; possible pronunciation/lexical issues do not prevent understanding.
- 0 points: The question is missing; OR it does not match the required content point; OR it is not grammatically a correct direct question; OR lexical/phonetic errors prevent communication.

Strict ЕГЭ notes:
- There are 4 questions, not 5.
- The required form is a direct question. For example, "Where is the clinic located?" is acceptable. A grammatically wrong direct-question word order should receive 0 for that question.
- Repeated errors are counted separately for separate questions.
- Introductory phrases are not required. If present, ignore them and grade only the questions.
- A natural optional word like "any" in "Are there any family discounts?" is recommended, but do not mark the question wrong only because "any" is absent if the question is otherwise grammatical and clear.

Feedback requirements for Task 2:
- Feedback must be in Russian and must be diagnostic, not just "wrong word order" plus a correction.
- For every question, mention whether the required content point is covered.
- If the question gets 0, identify all major language problems that affect the score: missing auxiliary/linking verb, wrong direct-question word order, missing/incorrect article, wrong preposition, wrong lexical choice, or content mismatch.
- Do not stop after the first error if there are several important errors.
- Distinguish error types precisely:
  * "Where the clinic located?" has the article "the", but it is missing the auxiliary/linking verb "is" after "where".
  * "How I can get there?" has incorrect direct-question word order; correct is "How can I get there?".
  * "Is there dentist at your clinic?" has correct inversion with "is there", but it is missing the article "a" before the singular countable noun "dentist".
- End each feedback item with one corrected version of the question.
"""
