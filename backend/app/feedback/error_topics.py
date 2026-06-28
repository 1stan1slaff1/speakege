from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.schemas import ErrorTopicResponse
from app.models.tables import ErrorTopic

ERROR_TOPIC_SEED_DATA = [
    # Task 2 / question formation
    {
        "id": "question_word_order",
        "title_ru": "Порядок слов в прямом вопросе",
        "short_explanation_ru": "В прямом вопросе вспомогательный глагол или глагол-связка обычно стоит перед подлежащим: Where is..., How can..., Do you...",
        "material_title": "Прямые вопросы в английском",
        "material_url": "/learn/direct-question-word-order",
        "category": "language",
        "applies_to_tasks": ["task2"],
        "display_order": 100,
    },
    {
        "id": "missing_auxiliary",
        "title_ru": "Вспомогательные глаголы в вопросах",
        "short_explanation_ru": "В вопросах часто нужен вспомогательный глагол do/does/did, модальный глагол или связка be перед подлежащим.",
        "material_title": "Do/does/did и be в вопросах",
        "material_url": "/learn/auxiliary-verbs-questions",
        "category": "language",
        "applies_to_tasks": ["task2"],
        "display_order": 110,
    },
    {
        "id": "there_is_are",
        "title_ru": "Конструкция there is / there are",
        "short_explanation_ru": "There is используется с единственным числом, there are — с множественным. В вопросе порядок: Is there...? / Are there...?",
        "material_title": "There is / there are",
        "material_url": "/learn/there-is-are",
        "category": "language",
        "applies_to_tasks": ["task2"],
        "display_order": 120,
    },
    {
        "id": "prepositions_transport",
        "title_ru": "Транспорт и предлоги",
        "short_explanation_ru": "В вопросах про транспорт часто используются by public transport, get to, go by bus/train, bus stop near the place.",
        "material_title": "Как спрашивать про транспорт",
        "material_url": "/learn/transport-questions",
        "category": "language",
        "applies_to_tasks": ["task2"],
        "display_order": 130,
    },
    {
        "id": "content_mismatch",
        "title_ru": "Несоответствие пункту задания",
        "short_explanation_ru": "Вопрос должен точно соответствовать указанному пункту: location, price, discounts, opening hours и т.д.",
        "material_title": "Как раскрывать пункты задания 2",
        "material_url": "/learn/task2-content-points",
        "category": "content",
        "applies_to_tasks": ["task2"],
        "display_order": 140,
    },
    {
        "id": "wrong_question_type",
        "title_ru": "Неверный тип вопроса",
        "short_explanation_ru": "В задании 2 нужен прямой вопрос. Косвенные или неполные формулировки часто повышают риск грамматической ошибки.",
        "material_title": "Прямой вопрос vs косвенный вопрос",
        "material_url": "/learn/direct-vs-indirect-questions",
        "category": "language",
        "applies_to_tasks": ["task2"],
        "display_order": 150,
    },
    {
        "id": "unclear_question",
        "title_ru": "Непонятная формулировка вопроса",
        "short_explanation_ru": "Вопрос должен быть понятным на слух и содержать достаточно слов, чтобы адресат понял, какую информацию вы запрашиваете.",
        "material_title": "Как делать вопрос понятным",
        "material_url": "/learn/clear-questions",
        "category": "language",
        "applies_to_tasks": ["task2"],
        "display_order": 160,
    },

    # Task 3 / interview answers
    {
        "id": "answer_too_short",
        "title_ru": "Развёрнутый ответ в 2–3 предложения",
        "short_explanation_ru": "В задании 3 короткого фрагмента или одного неполного предложения обычно недостаточно: нужен полный ответ на 2–3 содержательные фразы.",
        "material_title": "Как отвечать развёрнуто в задании 3",
        "material_url": "/learn/task3-full-answer",
        "category": "content",
        "applies_to_tasks": ["task3"],
        "display_order": 200,
    },
    {
        "id": "missing_second_part",
        "title_ru": "Ответ на обе части вопроса",
        "short_explanation_ru": "Если вопрос состоит из двух частей, нужно ответить на обе. Иначе ответ считается неполным.",
        "material_title": "Двухчастные вопросы в интервью",
        "material_url": "/learn/task3-two-part-questions",
        "category": "content",
        "applies_to_tasks": ["task3"],
        "display_order": 210,
    },
    {
        "id": "missing_reason",
        "title_ru": "Обоснование ответа на вопрос why",
        "short_explanation_ru": "Если в вопросе есть why, в ответе должна быть причина или объяснение.",
        "material_title": "Как давать reason в устном ответе",
        "material_url": "/learn/giving-reasons",
        "category": "content",
        "applies_to_tasks": ["task3"],
        "display_order": 220,
    },
    {
        "id": "off_topic_answer",
        "title_ru": "Ответ точно по вопросу",
        "short_explanation_ru": "Ответ должен соответствовать конкретному вопросу интервьюера, а не уходить в общий топик.",
        "material_title": "Как не уходить от темы в задании 3",
        "material_url": "/learn/task3-relevance",
        "category": "content",
        "applies_to_tasks": ["task3"],
        "display_order": 230,
    },

    # Task 4 / content
    {
        "id": "task4_project_connection",
        "title_ru": "Связь фотографий с темой проекта",
        "short_explanation_ru": "В начале ответа нужно показать, почему эти фотографии подходят к теме проекта, а не просто описать их.",
        "material_title": "Связь фото с проектом в задании 4",
        "material_url": "/learn/task4-project-connection",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 300,
    },
    {
        "id": "task4_photo_description",
        "title_ru": "Краткое описание обеих фотографий",
        "short_explanation_ru": "Нужно кратко описать обе фотографии так, чтобы друг понял, какие ситуации изображены.",
        "material_title": "Описание фото в задании 4",
        "material_url": "/learn/task4-photo-description",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 310,
    },
    {
        "id": "task4_meaningful_difference",
        "title_ru": "Значимое отличие между фотографиями",
        "short_explanation_ru": "Отличие должно быть связано с темой проекта, а не со случайными деталями вроде цвета одежды или количества людей.",
        "material_title": "Как сравнивать фотографии в задании 4",
        "material_url": "/learn/task4-meaningful-difference",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 320,
    },
    {
        "id": "task4_advantages",
        "title_ru": "Преимущества двух вариантов",
        "short_explanation_ru": "В задании 4 нужно назвать 1–2 преимущества вариантов, показанных на фото.",
        "material_title": "Advantages в задании 4",
        "material_url": "/learn/task4-advantages",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 330,
    },
    {
        "id": "task4_disadvantages",
        "title_ru": "Недостатки двух вариантов",
        "short_explanation_ru": "После преимуществ нужно назвать 1–2 недостатка вариантов, показанных на фото.",
        "material_title": "Disadvantages в задании 4",
        "material_url": "/learn/task4-disadvantages",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 340,
    },
    {
        "id": "task4_opinion",
        "title_ru": "Личное мнение по теме проекта",
        "short_explanation_ru": "Нужно явно сказать, какой вариант вы предпочитаете, выбрали бы или считаете более важным — в зависимости от формулировки задания.",
        "material_title": "Opinion в задании 4",
        "material_url": "/learn/task4-opinion",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 350,
    },
    {
        "id": "task4_reason_for_opinion",
        "title_ru": "Обоснование личного мнения",
        "short_explanation_ru": "Личное мнение должно быть объяснено: добавьте причину, почему вы выбираете этот вариант.",
        "material_title": "Как обосновать мнение в задании 4",
        "material_url": "/learn/task4-reason-for-opinion",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 360,
    },
    {
        "id": "task4_sentence_count",
        "title_ru": "Объём 12–15 фраз",
        "short_explanation_ru": "Для полного раскрытия задания 4 обычно нужно 12–15 фраз. Слишком короткий ответ не раскрывает коммуникативную задачу.",
        "material_title": "Объём ответа в задании 4",
        "material_url": "/learn/task4-sentence-count",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 370,
    },
    {
        "id": "task4_factual_mismatch",
        "title_ru": "Несоответствие изображению",
        "short_explanation_ru": "Описание не должно противоречить тому, что изображено на фотографии или указано в задании.",
        "material_title": "Фактическая точность в задании 4",
        "material_url": "/learn/task4-factual-mismatch",
        "category": "content",
        "applies_to_tasks": ["task4"],
        "display_order": 380,
    },

    # Task 4 / organisation
    {
        "id": "task4_greeting",
        "title_ru": "Обращение к другу в начале",
        "short_explanation_ru": "Задание требует голосовое сообщение другу, поэтому начало должно звучать как обращение: Hi, Alex! I’ve found two photos...",
        "material_title": "Формат voice message в задании 4",
        "material_url": "/learn/task4-voice-message-style",
        "category": "organisation",
        "applies_to_tasks": ["task4"],
        "display_order": 400,
    },
    {
        "id": "task4_closing",
        "title_ru": "Заключительная фраза",
        "short_explanation_ru": "В конце голосового сообщения нужна естественная завершающая фраза, например: Let me know what you think.",
        "material_title": "Заключение в задании 4",
        "material_url": "/learn/task4-closing",
        "category": "organisation",
        "applies_to_tasks": ["task4"],
        "display_order": 410,
    },
    {
        "id": "task4_linking",
        "title_ru": "Логические связки",
        "short_explanation_ru": "Используйте связки для перехода между описанием, отличиями, преимуществами, недостатками и мнением.",
        "material_title": "Связки для монолога",
        "material_url": "/learn/task4-linking",
        "category": "organisation",
        "applies_to_tasks": ["task4"],
        "display_order": 420,
    },
    {
        "id": "task4_logical_order",
        "title_ru": "Логичный порядок пунктов плана",
        "short_explanation_ru": "Ответ легче воспринимается, если идти по плану: связь с проектом, описание/отличия, преимущества, недостатки, мнение.",
        "material_title": "План ответа в задании 4",
        "material_url": "/learn/task4-answer-plan",
        "category": "organisation",
        "applies_to_tasks": ["task4"],
        "display_order": 430,
    },
    {
        "id": "task4_voice_message_style",
        "title_ru": "Стиль голосового сообщения",
        "short_explanation_ru": "Ответ должен звучать как сообщение другу, а не как формальное сравнение картинок.",
        "material_title": "Неформальный стиль voice message",
        "material_url": "/learn/task4-voice-message-style",
        "category": "organisation",
        "applies_to_tasks": ["task4"],
        "display_order": 440,
    },

    # Shared language topics
    {
        "id": "articles_singular_countable",
        "title_ru": "Артикли a/an с исчисляемыми существительными",
        "short_explanation_ru": "Если существительное в единственном числе и его можно посчитать, обычно нужен артикль a/an или другой определитель.",
        "material_title": "Артикли a/an в заданиях ЕГЭ",
        "material_url": "/learn/articles-a-an",
        "category": "language",
        "applies_to_tasks": ["task2", "task3", "task4"],
        "display_order": 600,
    },
    {
        "id": "plural_forms",
        "title_ru": "Единственное и множественное число",
        "short_explanation_ru": "Форма существительного должна совпадать с идеей ответа: discounts, classes, activities во множественном числе, если речь о нескольких вариантах.",
        "material_title": "Множественное число в устной части",
        "material_url": "/learn/plural-forms",
        "category": "language",
        "applies_to_tasks": ["task2", "task3", "task4"],
        "display_order": 610,
    },
    {
        "id": "prepositions_place",
        "title_ru": "Предлоги места",
        "short_explanation_ru": "Следите за выражениями вроде located in/at, in the picture, at school, in a park.",
        "material_title": "Предлоги места",
        "material_url": "/learn/prepositions-place",
        "category": "language",
        "applies_to_tasks": ["task2", "task3", "task4"],
        "display_order": 620,
    },
    {
        "id": "basic_grammar_error",
        "title_ru": "Базовая грамматика в устном ответе",
        "short_explanation_ru": "Грубые ошибки базового уровня могут привести к потере балла даже при понятной идее ответа.",
        "material_title": "Типичные грамматические ошибки в говорении",
        "material_url": "/learn/basic-speaking-grammar",
        "category": "language",
        "applies_to_tasks": ["task3", "task4"],
        "display_order": 630,
    },
    {
        "id": "subject_verb_agreement",
        "title_ru": "Согласование подлежащего и сказуемого",
        "short_explanation_ru": "В Present Simple нужно следить за формами вроде I live, he lives, people are, it is.",
        "material_title": "Subject-verb agreement",
        "material_url": "/learn/subject-verb-agreement",
        "category": "language",
        "applies_to_tasks": ["task3", "task4"],
        "display_order": 640,
    },
    {
        "id": "tense_choice",
        "title_ru": "Выбор времени глагола",
        "short_explanation_ru": "Выбирайте время по смыслу: настоящее для привычек, прошедшее для прошлого опыта, будущее для планов.",
        "material_title": "Времена в устном ответе ЕГЭ",
        "material_url": "/learn/speaking-tenses",
        "category": "language",
        "applies_to_tasks": ["task3", "task4"],
        "display_order": 650,
    },
    {
        "id": "lexical_choice",
        "title_ru": "Выбор слов и естественные выражения",
        "short_explanation_ru": "Неверный выбор слова или неестественное выражение может сделать ответ менее точным или непонятным.",
        "material_title": "Лексика для устной части",
        "material_url": "/learn/speaking-vocabulary",
        "category": "language",
        "applies_to_tasks": ["task3", "task4"],
        "display_order": 660,
    },
    {
        "id": "unclear_answer",
        "title_ru": "Понятность ответа",
        "short_explanation_ru": "Ответ должен быть достаточно ясным: избегайте набора слов, незаконченных фраз и слишком резких переходов.",
        "material_title": "Как сделать устный ответ понятным",
        "material_url": "/learn/clear-speaking-answer",
        "category": "language",
        "applies_to_tasks": ["task3", "task4"],
        "display_order": 670,
    },
]


def error_topic_to_response(topic: ErrorTopic) -> ErrorTopicResponse:
    return ErrorTopicResponse(
        id=topic.id,
        title_ru=topic.title_ru,
        short_explanation_ru=topic.short_explanation_ru,
        material_title=topic.material_title,
        material_url=topic.material_url,
        category=topic.category,
        applies_to_tasks=topic.applies_to_tasks or [],
        display_order=topic.display_order,
    )


def list_active_error_topics(db: Session, *, task_type: str | None = None) -> list[ErrorTopicResponse]:
    topics = list(
        db.scalars(
            select(ErrorTopic)
            .where(ErrorTopic.is_active.is_(True))
            .order_by(ErrorTopic.display_order.asc(), ErrorTopic.id.asc())
        )
    )
    if task_type:
        topics = [
            topic for topic in topics
            if task_type in (topic.applies_to_tasks or [])
        ]
    return [error_topic_to_response(topic) for topic in topics]


def upsert_error_topic(db: Session, data: dict) -> ErrorTopic:
    topic = db.get(ErrorTopic, data["id"])
    if topic:
        topic.title_ru = data["title_ru"]
        topic.short_explanation_ru = data["short_explanation_ru"]
        topic.material_title = data.get("material_title")
        topic.material_url = data.get("material_url")
        topic.category = data.get("category", "language")
        topic.applies_to_tasks = data.get("applies_to_tasks", [])
        topic.display_order = data.get("display_order", 1000)
        topic.is_active = True
    else:
        topic = ErrorTopic(
            id=data["id"],
            title_ru=data["title_ru"],
            short_explanation_ru=data["short_explanation_ru"],
            material_title=data.get("material_title"),
            material_url=data.get("material_url"),
            category=data.get("category", "language"),
            applies_to_tasks=data.get("applies_to_tasks", []),
            display_order=data.get("display_order", 1000),
            is_active=True,
        )
        db.add(topic)

    db.commit()
    db.refresh(topic)
    return topic
