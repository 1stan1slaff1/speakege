"""Email policy: Russian domains only (law 406-FZ), plus-tag stripping."""

ALLOWED_EMAIL_DOMAINS = frozenset(
    {
        "yandex.ru",
        "ya.ru",
        "yandex.by",
        "yandex.kz",
        "mail.ru",
        "inbox.ru",
        "list.ru",
        "bk.ru",
        "internet.ru",
        "rambler.ru",
        "vk.com",
    }
)

RUSSIAN_EMAIL_ERROR = (
    "Для регистрации нужна российская почта "
    "(Яндекс, Mail.ru, Рамблер, VK) — требование закона."
)


def normalize_email(email: str) -> str:
    """Trim, lowercase, strip plus-tags (user+tag@ == user@)."""
    local, _, domain = email.strip().lower().partition("@")
    local = local.split("+", 1)[0]
    return f"{local}@{domain}" if domain else local


def ensure_russian_email(email: str) -> str:
    """Return normalized email or raise ValueError with a user-facing message."""
    normalized = normalize_email(email)
    domain = normalized.rsplit("@", 1)[-1]
    if domain not in ALLOWED_EMAIL_DOMAINS:
        raise ValueError(RUSSIAN_EMAIL_ERROR)
    return normalized
