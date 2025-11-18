import re
from typing import Tuple

ALLOWED_EMAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "outlook.com",
    "hotmail.com",
    "hotmail.ru",
    "live.com",
    "msn.com",
    "yandex.ru",
    "yandex.com",
    "ya.ru",
    "mail.ru",
    "inbox.ru",
    "list.ru",
    "bk.ru",
    "yahoo.com",
    "yahoo.ru",
    "ymail.com",
    "protonmail.com",
    "pm.me",
    "tutanota.com",
    "zoho.com",
    "fastmail.com",
    "proton.me",
    "icloud.com",
    "me.com",
    "mac.com",
    "aol.com",
    "aol.ru",
    "rambler.ru",
    "pochta.ru",
    "e1.ru",
    "fromru.com",
    "qip.ru",
    "mail.ua",
    "meta.ua",
    "i.ua",
    "ukr.net",
    "bigmir.net",
    "3g.ua",
    "y.ua",
}

EMAIL_LOCAL_PART_PATTERN = re.compile(r"^[A-Za-z0-9._+-]+$")
EMAIL_DOMAIN_PATTERN = re.compile(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# Запрещенные слова в email
FORBIDDEN_EMAIL_PATTERNS = [
    r"admin",
    r"administrator",
    r"root",
    r"support",
    r"bot",
    r"demo",
    r"noreply",
    r"no-reply",
    r"donotreply",
    r"bounce",
    r"mailer",
    r"mail",
    r"contact",
    r"info",
    r"webmaster",
    r"abuse",
    r"postmaster",
    r"hostmaster",
    r"system",
    r"sysadmin",
    r"server",
    r"api",
    r"smtp",
    r"pop",
    r"imap",
]


def validate_email_chars(email: str) -> Tuple[bool, str]:
    """
    Строгая валидация символов в email
    """
    if not email or not isinstance(email, str):
        return False, "Email не может быть пустым"

    email = email.strip()
    if not email:
        return False, "Email не может быть пустым"

    if len(email) > 254:  # RFC 2821 limit
        return False, "Email слишком длинный"

    # Проверяем основной формат
    if "@" not in email:
        return False, "Некорректный формат email"

    local_part, domain = email.split("@", 1)

    # Проверяем локальную часть
    if not local_part:
        return False, "Отсутствует локальная часть email"

    if len(local_part) > 64:  # RFC 2821 limit
        return False, "Локальная часть email слишком длинная"

    if not local_part[0].isalnum() or not local_part[-1].isalnum():
        return (
            False,
            "Локальная часть должна начинаться и заканчиваться буквой или цифрой",
        )

    if ".." in local_part:
        return False, "Локальная часть не может содержать двойные точки"

    if local_part.startswith(".") or local_part.endswith("."):
        return False, "Локальная часть не может начинаться или заканчиваться точкой"

    if not EMAIL_LOCAL_PART_PATTERN.fullmatch(local_part):
        return False, "Локальная часть содержит недопустимые символы"

    # Проверяем домен
    if not domain:
        return False, "Отсутствует домен email"

    if len(domain) > 253:
        return False, "Домен email слишком длинный"

    if not EMAIL_DOMAIN_PATTERN.fullmatch(domain):
        return False, "Некорректный формат домена"

    # Проверяем подозрительные паттерны
    for forbidden in FORBIDDEN_EMAIL_PATTERNS:
        if re.search(forbidden, local_part, re.IGNORECASE):
            return False, "Email содержит запрещенные слова"

    return True, "Email валиден"


def is_allowed_email_domain(email: str) -> bool:
    if not email or "@" not in email:
        return False

    # Сначала проверим символы
    is_valid, error_msg = validate_email_chars(email)
    if not is_valid:
        return False

    local_part, domain = email.split("@", 1)
    local_part = local_part.strip()
    domain = domain.lower().strip()

    # Проверяем домен в списке разрешенных
    if domain not in ALLOWED_EMAIL_DOMAINS:
        return False

    return bool(local_part and EMAIL_LOCAL_PART_PATTERN.fullmatch(local_part))


def get_allowed_domains_list() -> list:
    return sorted(ALLOWED_EMAIL_DOMAINS)


def get_allowed_domains_display() -> str:
    popular = ["gmail.com", "yandex.ru", "mail.ru", "outlook.com", "yahoo.com"]
    return ", ".join(popular) + " и другие популярные сервисы"
