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


def task1_prompt(text: str) -> str:
    return f"""Task 1. You are going to read the text aloud. You have 1.5 minutes to read the text silently, then be ready to read it aloud. Remember that you will not have more than 1.5 minutes for reading aloud.

{text}"""


def make_task1_question(question_id: str, text: str, *, position: int) -> Question:
    return Question(
        id=question_id,
        task_type="task1",
        prompt_text=task1_prompt(text),
        reference_text=text,
        audio=QuestionAudio(intro="/audio/ege/task1/intro.mp3"),
        prep_seconds=90,
        record_seconds=90,
    )


def make_task2_question(
    question_id: str,
    *,
    variant: int,
    advertisement_title: str,
    advertisement_subtitle: str,
    context: str,
    prompts: list[str],
) -> Question:
    prompt_lines = "\n".join(f"{index}) {point}" for index, point in enumerate(prompts, start=1))
    return Question(
        id=question_id,
        task_type="task2",
        prompt_text=f"""Task 2. Study the advertisement.

{advertisement_title}
{advertisement_subtitle}

{context} In 1.5 minutes you are to ask four direct questions to find out about the following:

{prompt_lines}

You have 20 seconds to ask each question.""",
        task2_prompts=prompts,
        audio=QuestionAudio(
            intro=f"/audio/ege/task2/variant{variant:02d}/intro.mp3",
            question_cues=[
                f"/audio/ege/task2/variant{variant:02d}/q1.mp3",
                f"/audio/ege/task2/variant{variant:02d}/q2.mp3",
                f"/audio/ege/task2/variant{variant:02d}/q3.mp3",
                f"/audio/ege/task2/variant{variant:02d}/q4.mp3",
            ],
        ),
        prep_seconds=90,
        record_seconds=80,
    )


def task3_grading_prompt(topic: str, intro: str, questions: list[str]) -> str:
    return f"""Task 3. You are going to give an interview. You have to answer five questions. Give full answers to the questions: 2–3 sentences. Remember that you have 40 seconds to answer each question.

Interviewer intro:
{intro}

Questions:
{chr(10).join(f'{index + 1}) {question}' for index, question in enumerate(questions))}"""


def make_task3_question(question_id: str, *, variant: int, topic: str, questions: list[str]) -> Question:
    intro = f"Hello! It's Teenagers Round the World Channel. Our guest today is a teenager from Russia and we are going to discuss {topic}. Please answer five questions. So, let's get started."
    return Question(
        id=question_id,
        task_type="task3",
        prompt_text="""Task 3. You are going to give an interview. You have to answer five questions.

Give full answers to the questions: 2–3 sentences.

Remember that you have 40 seconds to answer each question.

The questions are played by the interviewer and are not shown on the screen, closer to the real exam format.""",
        grading_prompt_text=task3_grading_prompt(topic, intro, questions),
        interviewer_intro=intro,
        interview_questions=questions,
        audio=QuestionAudio(
            intro=f"/audio/ege/task3/variant{variant:02d}/intro.mp3",
            question_cues=[
                f"/audio/ege/task3/variant{variant:02d}/q1.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q2.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q3.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q4.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q5.mp3",
            ],
            end="/audio/ege/common/interview_end.mp3",
        ),
        prep_seconds=0,
        record_seconds=200,
    )


def make_task4_question(
    question_id: str,
    *,
    variant: int,
    project_title: str,
    photo1: str,
    photo2: str,
    advantages_phrase: str,
    disadvantages_phrase: str,
    opinion_phrase: str,
    image1: str,
    image2: str,
) -> Question:
    prompt_text = f"""Task 4. Imagine that you and your friend are doing a school project “{project_title}”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

In 2.5 minutes be ready to:

• explain the choice of the illustrations for the project by briefly describing them and noting the differences;
• mention the advantages (1–2) of {advantages_phrase};
• mention the disadvantages (1–2) of {disadvantages_phrase};
• express your opinion on the subject of the project — {opinion_phrase}.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously."""
    grading_prompt = f"""Task 4. Imagine that you and your friend are doing a school project “{project_title}”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

Photo 1: {photo1}.
Photo 2: {photo2}.

In 2.5 minutes be ready to:
- explain the choice of the illustrations for the project by briefly describing them and noting the differences;
- mention the advantages (1–2) of {advantages_phrase};
- mention the disadvantages (1–2) of {disadvantages_phrase};
- express your opinion on the subject of the project — {opinion_phrase}.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously."""
    return Question(
        id=question_id,
        task_type="task4",
        prompt_text=prompt_text,
        grading_prompt_text=grading_prompt,
        image_urls=[image1, image2],
        image_captions=["Photo 1", "Photo 2"],
        audio=QuestionAudio(
            intro=f"/audio/ege/task4/variant{variant:02d}/intro.mp3",
            start_cue="/audio/ege/common/start_speaking.mp3",
        ),
        prep_seconds=150,
        record_seconds=180,
    )


TASK1_TEXTS = {
    "snowflakes": """Snowflakes are ice crystals which fall through the Earth's atmosphere as snow. People like to think that every snowflake has a unique shape. However, it is not true. While snowflakes may look different, they can still be classified into eight groups and about eighty different variants. Some scientists have done a lot of research into making a kind of catalogue of snowflakes.

The most typical patterns for a snowflake are needles, columns, plates and rimes. The shape and the pattern of a snowflake largely depend on the weather conditions. The study of snowflakes has identified that long, thin needle-like ice crystals form at around zero, while a lower temperature will lead to very flat crystals. Further changes in temperature as a snowflake falls determine more complicated shapes of snowflakes. The size of a snowflake also depends on the air temperature.""",
    "urban_trees": """Urban trees are more important than many people think. In summer, streets with trees are usually cooler than streets without them. Leaves give shade and also release water into the air, which helps reduce heat. Trees can also improve air quality because they catch dust and absorb some harmful gases. In busy cities this is especially useful near roads and schools.

Another benefit of urban trees is psychological. Studies show that people often feel calmer and more focused when they can see green spaces from their windows. Even a small park can make a neighbourhood more pleasant. However, city trees need regular care. Their roots may be damaged by roads, and young trees need enough water. If cities want to become healthier places, planting and protecting trees should be part of long-term planning.""",
    "ocean_currents": """Ocean currents are large movements of water that travel through the seas. Some currents move near the surface, while others flow deep below. They are caused by wind, differences in water temperature, the amount of salt in the water and the rotation of the Earth. Although currents may seem far away from everyday life, they influence the climate of many countries.

Warm currents can make coastal areas milder in winter, while cold currents may cool the air above them. Currents also carry nutrients, which are important for fish and other sea animals. That is why some fishing areas are especially rich. Today scientists study ocean currents very carefully because climate change can affect their speed and direction. Even small changes in these systems may have serious consequences for weather, sea life and people living near the coast.""",
    "honeybees": """Honeybees are famous for producing honey, but their role in nature is much wider. When bees fly from flower to flower, they carry pollen. This process helps many plants produce fruit and seeds. Without bees and other pollinating insects, people would have fewer apples, berries, vegetables and nuts.

Bees live in organised colonies. Each bee has a role, and the colony works as one system. Worker bees collect food, care for young bees and protect the hive. Bees can also communicate with each other. When a worker bee finds a good source of food, it performs a special movement called a waggle dance. This dance tells other bees the direction and distance to the flowers. Unfortunately, bee populations are under pressure because of pesticides, diseases and loss of natural habitats. Protecting bees means protecting food production and biodiversity.""",
    "public_libraries": """Public libraries have changed a lot over the last century. In the past, people mainly visited libraries to borrow books or read newspapers. Today libraries still offer books, but they also provide access to computers, online databases, language courses and cultural events. For many people, a library is one of the few quiet places where they can study or work for free.

Libraries are especially important for children and teenagers. They help young people discover reading and learn how to search for reliable information. Librarians can recommend books, explain how to use digital resources and organise educational activities. In small towns, a library may also become a community centre where people meet and share ideas. Even in the age of the Internet, public libraries remain valuable because they give equal access to knowledge.""",
}

TASK4_IMAGES = {
    "weekend_1": make_svg_data_uri("Photo 1", "Family picnic in a park", "#dcfce7", "#22c55e"),
    "weekend_2": make_svg_data_uri("Photo 2", "Teenagers watching a film at home", "#dbeafe", "#3b82f6"),
    "fitness_1": make_svg_data_uri("Photo 1", "Jogging in a park", "#fef3c7", "#f59e0b"),
    "fitness_2": make_svg_data_uri("Photo 2", "Exercising in a gym", "#e0e7ff", "#6366f1"),
    "languages_1": make_svg_data_uri("Photo 1", "Language class", "#fce7f3", "#ec4899"),
    "languages_2": make_svg_data_uri("Photo 2", "Online lesson at home", "#ccfbf1", "#14b8a6"),
    "career_1": make_svg_data_uri("Photo 1", "Doctor in a clinic", "#fee2e2", "#ef4444"),
    "career_2": make_svg_data_uri("Photo 2", "Developer in an office", "#dbeafe", "#2563eb"),
    "eco_1": make_svg_data_uri("Photo 1", "Reusable water bottle", "#dcfce7", "#16a34a"),
    "eco_2": make_svg_data_uri("Photo 2", "Sorting rubbish for recycling", "#f0fdf4", "#22c55e"),
}

DEMO_QUESTIONS_BY_TASK_TYPE: dict[str, Question] = {
    "task1": make_task1_question("demo_task1_snowflakes_001", TASK1_TEXTS["snowflakes"], position=1),
    "task2": make_task2_question(
        "demo_task2_clinic_001",
        variant=1,
        advertisement_title="THE BEST CLINIC IN TOWN!",
        advertisement_subtitle="Professional care for the whole family!",
        context="You are considering visiting the clinic and now you would like to get more information.",
        prompts=["location", "public transport", "dentist", "family discounts"],
    ),
    "task3": make_task3_question(
        "demo_task3_accommodation_001",
        variant=1,
        topic="teenagers' attitude to their accommodation",
        questions=[
            "In what region do you live? Do you live in a big city, a town or in a village?",
            "Do you live in a flat or in a house? What is it like?",
            "What would you like to change about your flat or house? Why?",
            "What do you like and dislike about your neighbourhood?",
            "What kind of housing would you like to have in the future?",
        ],
    ),
    "task4": make_task4_question(
        "demo_task4_weekend_001",
        variant=1,
        project_title="Ideal weekend",
        photo1="a family is having a picnic in a park",
        photo2="two teenagers are watching a film at home",
        advantages_phrase="the two ways to spend the weekend",
        disadvantages_phrase="the two ways to spend the weekend",
        opinion_phrase="say which way of spending the weekend you prefer and why",
        image1=TASK4_IMAGES["weekend_1"],
        image2=TASK4_IMAGES["weekend_2"],
    ),
}

ADDITIONAL_CURATED_QUESTIONS: list[Question] = [
    make_task1_question("curated_task1_urban_trees_002", TASK1_TEXTS["urban_trees"], position=2),
    make_task1_question("curated_task1_ocean_currents_003", TASK1_TEXTS["ocean_currents"], position=3),
    make_task1_question("curated_task1_honeybees_004", TASK1_TEXTS["honeybees"], position=4),
    make_task1_question("curated_task1_public_libraries_005", TASK1_TEXTS["public_libraries"], position=5),
    make_task2_question(
        "curated_task2_sports_centre_002",
        variant=2,
        advertisement_title="ACTIVE LIFE SPORTS CENTRE",
        advertisement_subtitle="Fitness, swimming and team games for everyone!",
        context="You are considering visiting the sports centre and now you would like to get more information.",
        prompts=["location", "opening hours", "swimming pool", "family discounts"],
    ),
    make_task2_question(
        "curated_task2_bicycle_tour_003",
        variant=3,
        advertisement_title="CITY BIKE TOUR",
        advertisement_subtitle="See the city in a new way!",
        context="You are considering taking part in the bicycle tour and now you would like to get more information.",
        prompts=["starting point", "duration", "bike rental", "guide"],
    ),
    make_task2_question(
        "curated_task2_art_museum_004",
        variant=4,
        advertisement_title="MODERN ART MUSEUM",
        advertisement_subtitle="Discover young artists and new ideas!",
        context="You are considering visiting the art museum and now you would like to get more information.",
        prompts=["opening hours", "ticket price", "guided tours", "photo permission"],
    ),
    make_task2_question(
        "curated_task2_summer_camp_005",
        variant=5,
        advertisement_title="GREEN VALLEY SUMMER CAMP",
        advertisement_subtitle="Make friends and enjoy nature!",
        context="You are considering going to the summer camp and now you would like to get more information.",
        prompts=["dates", "accommodation", "activities", "transfer from the railway station"],
    ),
    make_task3_question(
        "curated_task3_hobbies_002",
        variant=2,
        topic="hobbies",
        questions=[
            "What hobbies are popular among teenagers in your region?",
            "What hobby do you have? How much time do you spend on it?",
            "Do you prefer hobbies that you can do alone or with other people? Why?",
            "Can hobbies help teenagers with their future career? Why or why not?",
            "What new hobby would you like to try in the future?",
        ],
    ),
    make_task3_question(
        "curated_task3_school_life_003",
        variant=3,
        topic="school life",
        questions=[
            "What subjects do you study at school this year?",
            "Which school subject do you find the most useful? Why?",
            "How much homework do you usually get? Is it too much in your opinion?",
            "What school event do you remember best? Why was it special?",
            "What would you change in your school if you could?",
        ],
    ),
    make_task3_question(
        "curated_task3_healthy_lifestyle_004",
        variant=4,
        topic="a healthy lifestyle",
        questions=[
            "What do teenagers in your region usually do to stay healthy?",
            "Do you do any sport or physical exercise? How often?",
            "What food do you think is healthy for teenagers? Why?",
            "Is it difficult for students to sleep enough during the school year? Why?",
            "What healthy habit would you like to develop in the future?",
        ],
    ),
    make_task3_question(
        "curated_task3_future_career_005",
        variant=5,
        topic="future careers",
        questions=[
            "What job would you like to have in the future?",
            "Who or what has influenced your career choice?",
            "What skills are important for your future profession? Why?",
            "Would you prefer to work alone or in a team? Why?",
            "Do you think teenagers should start thinking about their career early? Why or why not?",
        ],
    ),
    make_task4_question(
        "curated_task4_keeping_fit_002",
        variant=2,
        project_title="Keeping fit",
        photo1="a young man is jogging in a park",
        photo2="a young woman is exercising in a gym",
        advantages_phrase="the two ways of keeping fit",
        disadvantages_phrase="the two ways of keeping fit",
        opinion_phrase="say which way of keeping fit you prefer and why",
        image1=TASK4_IMAGES["fitness_1"],
        image2=TASK4_IMAGES["fitness_2"],
    ),
    make_task4_question(
        "curated_task4_learning_languages_003",
        variant=3,
        project_title="Learning languages",
        photo1="students are learning a foreign language in a classroom",
        photo2="a teenager is having an online language lesson at home",
        advantages_phrase="the two ways of learning languages",
        disadvantages_phrase="the two ways of learning languages",
        opinion_phrase="say which way of learning languages you prefer and why",
        image1=TASK4_IMAGES["languages_1"],
        image2=TASK4_IMAGES["languages_2"],
    ),
    make_task4_question(
        "curated_task4_future_career_004",
        variant=4,
        project_title="Choosing a future career",
        photo1="a doctor is talking to a patient in a clinic",
        photo2="a software developer is working at a computer in an office",
        advantages_phrase="the two jobs shown in the photos",
        disadvantages_phrase="the two jobs shown in the photos",
        opinion_phrase="say which job you would prefer and why",
        image1=TASK4_IMAGES["career_1"],
        image2=TASK4_IMAGES["career_2"],
    ),
    make_task4_question(
        "curated_task4_eco_habits_005",
        variant=5,
        project_title="Eco-friendly habits",
        photo1="a teenager is using a reusable water bottle",
        photo2="a family is sorting rubbish for recycling",
        advantages_phrase="the two eco-friendly habits shown in the photos",
        disadvantages_phrase="the two eco-friendly habits shown in the photos",
        opinion_phrase="say which habit is more important and why",
        image1=TASK4_IMAGES["eco_1"],
        image2=TASK4_IMAGES["eco_2"],
    ),
]

DEMO_QUESTIONS_BY_ID = {
    question.id: question
    for question in DEMO_QUESTIONS_BY_TASK_TYPE.values()
}

ALL_CURATED_QUESTIONS = [
    *DEMO_QUESTIONS_BY_TASK_TYPE.values(),
    *ADDITIONAL_CURATED_QUESTIONS,
]
ALL_CURATED_QUESTIONS_BY_ID = {
    question.id: question
    for question in ALL_CURATED_QUESTIONS
}


def get_demo_question(task_type: str) -> Question | None:
    return DEMO_QUESTIONS_BY_TASK_TYPE.get(task_type)


def get_question_by_id(question_id: str) -> Question | None:
    return ALL_CURATED_QUESTIONS_BY_ID.get(question_id)


def get_question_seed_items() -> list[tuple[Question, bool, int]]:
    seed_items: list[tuple[Question, bool, int]] = []
    for task_type, question in DEMO_QUESTIONS_BY_TASK_TYPE.items():
        seed_items.append((question, True, 1))

    for question in ADDITIONAL_CURATED_QUESTIONS:
        position = int(question.id.rsplit("_", 1)[-1]) if question.id.rsplit("_", 1)[-1].isdigit() else 100
        seed_items.append((question, False, position))

    return seed_items
