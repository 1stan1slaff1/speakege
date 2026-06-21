from urllib.parse import quote

from app.models.schemas import Question, QuestionAudio


def make_svg_data_uri(title: str, subtitle: str, background: str, accent: str) -> str:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
    <rect width="640" height="420" fill="{background}"/>
    <circle cx="520" cy="80" r="46" fill="{accent}" opacity="0.35"/>
    <rect x="70" y="255" width="500" height="72" rx="18" fill="#ffffff" opacity="0.88"/>
    <circle cx="210" cy="205" r="42" fill="#ffffff" opacity="0.82"/>
    <circle cx="315" cy="190" r="46" fill="#ffffff" opacity="0.82"/>
    <circle cx="425" cy="210" r="40" fill="#ffffff" opacity="0.82"/>
    <rect x="175" y="240" width="285" height="44" rx="18" fill="{accent}" opacity="0.72"/>
    <text x="320" y="350" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#1f2937">{title}</text>
    <text x="320" y="382" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#4b5563">{subtitle}</text>
  </svg>'''
    return f"data:image/svg+xml,{quote(svg)}"


TASK4_IMAGE_1 = make_svg_data_uri("Photo 1", "Family picnic in a park", "#dcfce7", "#22c55e")
TASK4_IMAGE_2 = make_svg_data_uri("Photo 2", "Teenagers watching a film at home", "#dbeafe", "#3b82f6")

TASK3_INTERVIEW_QUESTIONS = [
    "In what region do you live? Do you live in a big city, a town or in a village?",
    "Do you live in a flat or in a house? What is it like?",
    "What would you like to change about your flat or house? Why?",
    "What do you like and dislike about your neighbourhood?",
    "What kind of housing would you like to have in the future?",
]

TASK3_INTERVIEW_INTRO = "Hello! It's Teenagers Round the World Channel. Our guest today is a teenager from Russia and we are going to discuss teenagers' attitude to their accommodation. Please answer five questions. So, let's get started."

DEMO_QUESTIONS_BY_TASK_TYPE: dict[str, Question] = {
    "task1": Question(
        id="demo_task1_snowflakes_001",
        task_type="task1",
        prompt_text="""Task 1. You are going to read the text aloud. You have 1.5 minutes to read the text silently, then be ready to read it aloud. Remember that you will not have more than 1.5 minutes for reading aloud.

Snowflakes are ice crystals which fall through the Earth's atmosphere as snow. People like to think that every snowflake has a unique shape. However, it is not true. While snowflakes may look different, they can still be classified into eight groups and about eighty different variants. Some scientists have done a lot of research into making a kind of catalogue of snowflakes.

The most typical patterns for a snowflake are needles, columns, plates and rimes. The shape and the pattern of a snowflake largely depend on the weather conditions. The study of snowflakes has identified that long, thin needle-like ice crystals form at around zero, while a lower temperature will lead to very flat crystals. Further changes in temperature as a snowflake falls determine more complicated shapes of snowflakes. The size of a snowflake also depends on the air temperature.""",
        reference_text="""Snowflakes are ice crystals which fall through the Earth's atmosphere as snow. People like to think that every snowflake has a unique shape. However, it is not true. While snowflakes may look different, they can still be classified into eight groups and about eighty different variants. Some scientists have done a lot of research into making a kind of catalogue of snowflakes.

The most typical patterns for a snowflake are needles, columns, plates and rimes. The shape and the pattern of a snowflake largely depend on the weather conditions. The study of snowflakes has identified that long, thin needle-like ice crystals form at around zero, while a lower temperature will lead to very flat crystals. Further changes in temperature as a snowflake falls determine more complicated shapes of snowflakes. The size of a snowflake also depends on the air temperature.""",
        audio=QuestionAudio(
            intro="/audio/ege/task1/intro.mp3",
        ),
        prep_seconds=90,
        record_seconds=90,
    ),
    "task2": Question(
        id="demo_task2_clinic_001",
        task_type="task2",
        prompt_text="""Task 2. Study the advertisement.

THE BEST CLINIC IN TOWN!

You are considering visiting the clinic and now you would like to get more information. In 1.5 minutes you are to ask four direct questions to find out about the following:

1) location
2) public transport
3) dentist
4) family discounts

You have 20 seconds to ask each question.""",
        task2_prompts=["location", "public transport", "dentist", "family discounts"],
        audio=QuestionAudio(
            intro="/audio/ege/task2/variant01/intro.mp3",
            question_cues=[
                "/audio/ege/task2/variant01/q1.mp3",
                "/audio/ege/task2/variant01/q2.mp3",
                "/audio/ege/task2/variant01/q3.mp3",
                "/audio/ege/task2/variant01/q4.mp3",
            ],
        ),
        prep_seconds=90,
        record_seconds=80,
    ),
    "task3": Question(
        id="demo_task3_accommodation_001",
        task_type="task3",
        prompt_text="""Task 3. You are going to give an interview. You have to answer five questions.

Give full answers to the questions: 2–3 sentences.

Remember that you have 40 seconds to answer each question.

The questions are played by the interviewer and are not shown on the screen, closer to the real exam format.""",
        grading_prompt_text=f"""Task 3. You are going to give an interview. You have to answer five questions. Give full answers to the questions: 2–3 sentences. Remember that you have 40 seconds to answer each question.

Interviewer intro:
{TASK3_INTERVIEW_INTRO}

Questions:
{chr(10).join(f'{index + 1}) {question}' for index, question in enumerate(TASK3_INTERVIEW_QUESTIONS))}""",
        interviewer_intro=TASK3_INTERVIEW_INTRO,
        interview_questions=TASK3_INTERVIEW_QUESTIONS,
        audio=QuestionAudio(
            intro="/audio/ege/task3/variant01/intro.mp3",
            question_cues=[
                "/audio/ege/task3/variant01/q1.mp3",
                "/audio/ege/task3/variant01/q2.mp3",
                "/audio/ege/task3/variant01/q3.mp3",
                "/audio/ege/task3/variant01/q4.mp3",
                "/audio/ege/task3/variant01/q5.mp3",
            ],
            end="/audio/ege/common/interview_end.mp3",
        ),
        prep_seconds=0,
        record_seconds=200,
    ),
    "task4": Question(
        id="demo_task4_weekend_001",
        task_type="task4",
        prompt_text="""Task 4. Imagine that you and your friend are doing a school project “Ideal weekend”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

In 2.5 minutes be ready to:

• explain the choice of the illustrations for the project by briefly describing them and noting the differences;
• mention the advantages (1–2) of the two ways to spend the weekend;
• mention the disadvantages (1–2) of the two ways to spend the weekend;
• express your opinion on the subject of the project — say which way of spending the weekend presented in the pictures you prefer and why.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously.""",
        grading_prompt_text="""Task 4. Imagine that you and your friend are doing a school project “Ideal weekend”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

Photo 1: a family is having a picnic in a park.
Photo 2: two teenagers are watching a film at home.

In 2.5 minutes be ready to:
- explain the choice of the illustrations for the project by briefly describing them and noting the differences;
- mention the advantages (1–2) of the two ways to spend the weekend;
- mention the disadvantages (1–2) of the two ways to spend the weekend;
- express your opinion on the subject of the project — say which way of spending the weekend presented in the pictures you prefer and why.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously.""",
        image_urls=[TASK4_IMAGE_1, TASK4_IMAGE_2],
        image_captions=["Photo 1", "Photo 2"],
        audio=QuestionAudio(
            intro="/audio/ege/task4/variant01/intro.mp3",
            start_cue="/audio/ege/common/start_speaking.mp3",
        ),
        prep_seconds=150,
        record_seconds=180,
    ),
}

DEMO_QUESTIONS_BY_ID = {
    question.id: question
    for question in DEMO_QUESTIONS_BY_TASK_TYPE.values()
}


def get_demo_question(task_type: str) -> Question | None:
    return DEMO_QUESTIONS_BY_TASK_TYPE.get(task_type)


def get_question_by_id(question_id: str) -> Question | None:
    return DEMO_QUESTIONS_BY_ID.get(question_id)
