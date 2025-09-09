"""
Утилиты для фильтров шаблонов Jinja2
"""

import re
from markupsafe import Markup


def format_user_contact(user):
    """
    Форматирует контактную информацию пользователя для отображения в шаблонах
    """
    if user.email.endswith('@telegram.org'):
        telegram_id = user.email.replace('@telegram.org', '')
        return {
            'type': 'telegram',
            'display': f"TG: {telegram_id}",
            'value': telegram_id,
            'icon': 'fab fa-telegram',
            'link': f"tg://user?id={telegram_id}"
        }
    else:
        return {
            'type': 'email',
            'display': user.email,
            'value': user.email,
            'icon': 'fas fa-envelope',
            'link': f"mailto:{user.email}"
        }


def get_telegram_link(user):
    """
    Получает ссылку на Telegram пользователя
    """
    if user.email.endswith('@telegram.org'):
        telegram_id = user.email.replace('@telegram.org', '')
        return f"tg://user?id={telegram_id}"
    
    # Ищем связанного Telegram пользователя
    from app.models import TelegramUser
    telegram_user = TelegramUser.query.filter_by(user_id=user.id).first()
    if telegram_user:
        return f"tg://user?id={telegram_user.telegram_id}"
    
    return None


def make_links_clickable(text: str) -> Markup:
    """
    Преобразование ссылок в кликабельные с стилизацией и сокращением
    """
    if not text:
        return Markup("")
    
    # Ищем только https:// ссылки
    if 'https://' in text:
        # Простая замена - находим https:// и делаем ссылку до пробела
        parts = text.split('https://')
        if len(parts) > 1:
            result = parts[0]
            for part in parts[1:]:
                # Находим конец ссылки (пробел или конец строки)
                space_pos = part.find(' ')
                if space_pos == -1:
                    url = 'https://' + part
                    display_text = _shorten_url(url)
                    css_class = _get_link_class(url)
                    result += f'<a href="{url}" target="_blank" class="{css_class}" title="{url}">{display_text}</a>'
                else:
                    url = 'https://' + part[:space_pos]
                    display_text = _shorten_url(url)
                    css_class = _get_link_class(url)
                    result += f'<a href="{url}" target="_blank" class="{css_class}" title="{url}">{display_text}</a>' + part[space_pos:]
            return Markup(result)
    
    return Markup(text)


def _shorten_url(url: str) -> str:
    """
    Сокращает URL для отображения
    """
    # Убираем https://
    if url.startswith('https://'):
        url = url[8:]
    
    # Специальная обработка для GitHub Gist
    if url.startswith('gist.github.com/'):
        return 'gist.github.com'
    
    # Специальная обработка для других популярных сервисов
    if url.startswith('github.com/'):
        parts = url.split('/')
        if len(parts) >= 3:
            return f'github.com/{parts[1]}'
    
    if url.startswith('gitlab.com/'):
        parts = url.split('/')
        if len(parts) >= 3:
            return f'gitlab.com/{parts[1]}'
    
    if url.startswith('bitbucket.org/'):
        parts = url.split('/')
        if len(parts) >= 3:
            return f'bitbucket.org/{parts[1]}'
    
    # Для остальных ссылок берем только домен
    if '/' in url:
        return url.split('/')[0]
    
    return url


def _get_link_class(url: str) -> str:
    """
    Определяет CSS класс для ссылки
    """
    if 'gist.github.com' in url:
        return 'external-link gist-link'
    
    return 'external-link'


def format_description(text: str) -> Markup:
    """
    Форматирует описание материала с поддержкой ссылок и переносов строк
    
    Args:
        text: Текст описания
        
    Returns:
        Markup: Отформатированный HTML
    """
    if not text:
        return Markup("")
    
    # Сначала делаем ссылки кликабельными
    text_with_links = make_links_clickable(text)
    
    # Заменяем экранированные \n на реальные переносы строк, затем на <br>
    text_with_breaks = str(text_with_links).replace('\\n', '\n').replace('\n', '<br>')
    
    return Markup(text_with_breaks)


def smart_truncate(text: str, length: int = 60) -> Markup:
    """
    Простое обрезание текста
    """
    if not text:
        return Markup("")
    
    # Просто обрезаем и добавляем многоточие
    if len(text) > length:
        return Markup(text[:length] + "...")
    
    return Markup(text)


def extract_filename(file_path: str) -> str:
    """
    Извлекает только имя файла из пути
    Например: "14/1.pdf" -> "1.pdf"
    """
    if not file_path:
        return ""
    
    # Разделяем по слешу и берем последнюю часть
    return file_path.split('/')[-1]


def get_cdn_url(file_path: str, subject_id: int) -> str:
    """
    Генерирует URL для CDN
    Например: "14/1.pdf" + subject_id=14 -> "http://cdn.localhost:5001/14/1.pdf"
    """
    if not file_path:
        return ""
    
    # Извлекаем только имя файла
    filename = extract_filename(file_path)
    
    # Возвращаем CDN URL
    return f"http://cdn.localhost:5001/{subject_id}/{filename}"


def get_cdn_url_production(file_path: str, subject_id: int) -> str:
    """
    Генерирует URL для CDN в продакшене
    """
    if not file_path:
        return ""
    
    filename = extract_filename(file_path)
    return f"https://cdn.yourdomain.com/{subject_id}/{filename}"