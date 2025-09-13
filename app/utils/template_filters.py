from markupsafe import Markup, escape


def format_user_contact(user):
    if user.email.endswith("@telegram.org"):
        telegram_id = user.email.replace("@telegram.org", "")
        return {
            "type": "telegram",
            "display": f"TG: {telegram_id}",
            "value": telegram_id,
            "icon": "fab fa-telegram",
            "link": f"tg://user?id={telegram_id}",
        }
    else:
        return {
            "type": "email",
            "display": user.email,
            "value": user.email,
            "icon": "fas fa-envelope",
            "link": f"mailto:{user.email}",
        }


def get_telegram_link(user):
    if user.email.endswith("@telegram.org"):
        telegram_id = user.email.replace("@telegram.org", "")
        return f"tg://user?id={telegram_id}"

    from app.models import TelegramUser

    telegram_user = TelegramUser.query.filter_by(user_id=user.id).first()
    if telegram_user:
        return f"tg://user?id={telegram_user.telegram_id}"

    return None


def make_links_clickable(text: str) -> str:
    if not text:
        return ""

    if "https://" in text:
        parts = text.split("https://")
        if len(parts) > 1:
            result = parts[0] if parts[0] else ""
            for part in parts[1:]:
                space_pos = part.find(" ")
                if space_pos == -1:
                    url = "https://" + part
                    display_text = _shorten_url(url)
                    css_class = _get_link_class(url)
                    safe_url = url.replace('"', '&quot;').replace("'", '&#x27;')
                    result += f'<a href="{safe_url}" target="_blank" class="{css_class}" title="{safe_url}">{display_text}</a>'
                else:
                    url = "https://" + part[:space_pos]
                    display_text = _shorten_url(url)
                    css_class = _get_link_class(url)
                    safe_url = url.replace('"', '&quot;').replace("'", '&#x27;')
                    result += (
                        f'<a href="{safe_url}" target="_blank" class="{css_class}" title="{safe_url}">{display_text}</a>'
                        + part[space_pos:]
                    )
            return result

    return escape(text)


def _shorten_url(url: str) -> str:
    # Безопасная обработка URL
    if not url or not isinstance(url, str):
        return ""

    # Очищаем URL от потенциально опасных символов
    url = url.strip()

    # Разрешенные домены
    allowed_domains = [
        "gist.github.com",
        "github.com",
        "gitlab.com",
        "bitbucket.org",
    ]

    # Удаляем протокол если есть
    if url.startswith("https://"):
        url = url[8:]

    # Проверяем, что URL начинается с разрешенного домена
    is_allowed = any(url.startswith(domain) for domain in allowed_domains)
    if not is_allowed:
        # Если домен не разрешен, возвращаем только домен
        if "/" in url:
            return url.split("/")[0]
        return url

    # Обрабатываем gist.github.com ссылки
    if url.startswith("gist.github.com/"):
        return "gist.github.com"

    # Обрабатываем github.com ссылки
    if url.startswith("github.com/"):
        parts = url.split("/")
        if len(parts) >= 3:
            # Безопасно экранируем имя пользователя
            username = (
                parts[1]
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            return f"github.com/{username}"

    # Обрабатываем gitlab.com ссылки
    if url.startswith("gitlab.com/"):
        parts = url.split("/")
        if len(parts) >= 3:
            # Безопасно экранируем имя пользователя
            username = (
                parts[1]
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            return f"gitlab.com/{username}"

    # Обрабатываем bitbucket.org ссылки
    if url.startswith("bitbucket.org/"):
        parts = url.split("/")
        if len(parts) >= 3:
            # Безопасно экранируем имя пользователя
            username = (
                parts[1]
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            return f"bitbucket.org/{username}"

    # Для остальных случаев возвращаем только домен
    if "/" in url:
        return url.split("/")[0]

    return url


def _get_link_class(url: str) -> str:
    if "gist.github.com" in url:
        return "external-link gist-link"

    return "external-link"


def format_description(text: str) -> str:
    if not text:
        return ""

    # Сначала обрабатываем ссылки, потом экранируем остальной текст
    text_with_links = make_links_clickable(text)

    text_with_breaks = (
        str(text_with_links).replace("\\n", "\n").replace("\n", "<br>")
    )

    return text_with_breaks


def smart_truncate(text: str, length: int = 60) -> Markup:
    if not text:
        return Markup("")  # nosec

    # Экранируем текст для безопасности
    escaped_text = escape(text)

    if len(escaped_text) > length:
        return Markup(escaped_text[:length] + "...")  # nosec

    return Markup(escaped_text)  # nosec


def extract_filename(file_path: str) -> str:
    if not file_path:
        return ""

    return file_path.split("/")[-1]


def get_cdn_url(file_path: str, subject_id: int) -> str:
    if not file_path:
        return ""

    filename = extract_filename(file_path)

    return f"http://cdn.localhost:5001/{subject_id}/{filename}"


def get_cdn_url_production(file_path: str, subject_id: int) -> str:
    if not file_path:
        return ""

    filename = extract_filename(file_path)
    return f"https://cdn.yourdomain.com/{subject_id}/{filename}"