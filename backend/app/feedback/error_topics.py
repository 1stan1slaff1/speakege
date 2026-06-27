from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.schemas import ErrorTopicResponse
from app.models.tables import ErrorTopic

ERROR_TOPIC_SEED_DATA = [
    {
        "id": "question_word_order",
        "title_ru": "Порядок слов в прямом вопросе",
        "short_explanation_ru": "В прямом вопросе вспомогательный глагол или глагол-связка обычно стоит перед подлежащим: Where is..., How can..., Do you...",
        "material_title": "Прямые вопросы в английском",
        "material_url": "/learn/direct-question-word-order",
    },
    {
        "id": "missing_auxiliary",
        "title_ru": "Вспомогательные глаголы в вопросах",
        "short_explanation_ru": "В вопросах часто нужен вспомогательный глагол do/does/did, модальный глагол или связка be перед подлежащим.",
        "material_title": "Do/does/did и be в вопросах",
        "material_url": "/learn/auxiliary-verbs-questions",
    },
    {
        "id": "articles_singular_countable",
        "title_ru": "Артикли a/an с исчисляемыми существительными",
        "short_explanation_ru": "Если существительное в единственном числе и его можно посчитать, обычно нужен артикль a/an или другой определитель.",
        "material_title": "Артикли a/an в заданиях ЕГЭ",
        "material_url": "/learn/articles-a-an",
    },
    {
        "id": "there_is_are",
        "title_ru": "Конструкция there is / there are",
        "short_explanation_ru": "There is используется с единственным числом, there are — с множественным. В вопросе порядок: Is there...? / Are there...?",
        "material_title": "There is / there are",
        "material_url": "/learn/there-is-are",
    },
    {
        "id": "prepositions_place",
        "title_ru": "Предлоги места",
        "short_explanation_ru": "Для location часто нужны выражения вроде located in/at, near, next to. Неверный предлог может сделать вопрос неестественным или непонятным.",
        "material_title": "Предлоги места",
        "material_url": "/learn/prepositions-place",
    },
    {
        "id": "prepositions_transport",
        "title_ru": "Транспорт и предлоги",
        "short_explanation_ru": "В вопросах про транспорт часто используются by public transport, get to, go by bus/train, bus stop near the place.",
        "material_title": "Как спрашивать про транспорт",
        "material_url": "/learn/transport-questions",
    },
    {
        "id": "plural_forms",
        "title_ru": "Единственное и множественное число",
        "short_explanation_ru": "Форма существительного должна совпадать с идеей вопроса: discounts, classes, activities во множественном числе, если речь о нескольких вариантах.",
        "material_title": "Множественное число в вопросах",
        "material_url": "/learn/plural-forms",
    },
    {
        "id": "content_mismatch",
        "title_ru": "Несоответствие пункту задания",
        "short_explanation_ru": "Вопрос должен точно соответствовать указанному пункту: location, price, discounts, opening hours и т.д.",
        "material_title": "Как раскрывать пункты задания 2",
        "material_url": "/learn/task2-content-points",
    },
    {
        "id": "wrong_question_type",
        "title_ru": "Неверный тип вопроса",
        "short_explanation_ru": "В задании 2 нужен прямой вопрос. Косвенные или неполные формулировки часто повышают риск грамматической ошибки.",
        "material_title": "Прямой вопрос vs косвенный вопрос",
        "material_url": "/learn/direct-vs-indirect-questions",
    },
    {
        "id": "unclear_question",
        "title_ru": "Непонятная формулировка вопроса",
        "short_explanation_ru": "Вопрос должен быть понятным на слух и содержать достаточно слов, чтобы адресат понял, какую информацию вы запрашиваете.",
        "material_title": "Как делать вопрос понятным",
        "material_url": "/learn/clear-questions",
    },
]


def error_topic_to_response(topic: ErrorTopic) -> ErrorTopicResponse:
    return ErrorTopicResponse(
        id=topic.id,
        title_ru=topic.title_ru,
        short_explanation_ru=topic.short_explanation_ru,
        material_title=topic.material_title,
        material_url=topic.material_url,
    )


def list_active_error_topics(db: Session) -> list[ErrorTopicResponse]:
    topics = db.scalars(
        select(ErrorTopic)
        .where(ErrorTopic.is_active.is_(True))
        .order_by(ErrorTopic.id.asc())
    )
    return [error_topic_to_response(topic) for topic in topics]


def upsert_error_topic(db: Session, data: dict) -> ErrorTopic:
    topic = db.get(ErrorTopic, data["id"])
    if topic:
        topic.title_ru = data["title_ru"]
        topic.short_explanation_ru = data["short_explanation_ru"]
        topic.material_title = data.get("material_title")
        topic.material_url = data.get("material_url")
        topic.is_active = True
    else:
        topic = ErrorTopic(
            id=data["id"],
            title_ru=data["title_ru"],
            short_explanation_ru=data["short_explanation_ru"],
            material_title=data.get("material_title"),
            material_url=data.get("material_url"),
            is_active=True,
        )
        db.add(topic)

    db.commit()
    db.refresh(topic)
    return topic
