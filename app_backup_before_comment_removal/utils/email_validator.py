import re


ALLOWED_EMAIL_DOMAINS = {
    # Google
    "gmail.com",
    "googlemail.com",
    # Microsoft
    "outlook.com",
    "hotmail.com",
    "hotmail.ru",
    "live.com",
    "msn.com",
    # Yandex
    "yandex.ru",
    "yandex.com",
    "ya.ru",
    # Mail.ru
    "mail.ru",
    "inbox.ru",
    "list.ru",
    "bk.ru",
    # Yahoo
    "yahoo.com",
    "yahoo.ru",
    "ymail.com",
}


EMAIL_LOCAL_PART_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё0-9._-]+$")


def is_allowed_email_domain(email: str) -> bool:
    if not email or "@" not in email:
        return False

    local_part, domain = email.split("@", 1)
    local_part = local_part.strip()
    domain = domain.lower().strip()

    if domain not in ALLOWED_EMAIL_DOMAINS:
        return False

    return bool(local_part and EMAIL_LOCAL_PART_PATTERN.fullmatch(local_part))


def get_allowed_domains_list() -> list:
    return sorted(ALLOWED_EMAIL_DOMAINS)


def get_allowed_domains_display() -> str:
    popular = ["gmail.com", "yandex.ru", "mail.ru", "outlook.com", "yahoo.com"]
    return ", ".join(popular) + " и другие популярные сервисы"

