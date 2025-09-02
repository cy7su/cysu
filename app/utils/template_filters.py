"""
Утилиты для фильтров шаблонов Jinja2
"""

import re
from markupsafe import Markup


def make_links_clickable(text: str) -> Markup:
    """
    Простое преобразование ссылок в кликабельные без обрезания
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
                    result += f'<a href="{url}" target="_blank">{url}</a>'
                else:
                    url = 'https://' + part[:space_pos]
                    result += f'<a href="{url}" target="_blank">{url}</a>' + part[space_pos:]
            return Markup(result)
    
    return Markup(text)


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
    
    # Заменяем переносы строк на <br>
    text_with_breaks = str(text_with_links).replace('\n', '<br>')
    
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