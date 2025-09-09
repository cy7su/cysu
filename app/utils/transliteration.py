"""
Утилиты для транслитерации русских символов в английские
"""

import re

def transliterate_russian_to_english(text: str) -> str:
    """
    Транслитерирует русские символы в английские

    Args:
        text: Текст для транслитерации

    Returns:
        str: Транслитерированный текст
    """
    if not text:
        return ""

    # Словарь транслитерации русских символов
    transliteration_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',

        # Заглавные буквы
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'J', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    result = ""
    for char in text:
        if char in transliteration_map:
            result += transliteration_map[char]
        else:
            result += char

    return result

def sanitize_filename(filename: str) -> str:
    """
    Очищает имя файла: транслитерирует русские символы, заменяет пробелы на подчеркивания,
    удаляет недопустимые символы

    Args:
        filename: Исходное имя файла

    Returns:
        str: Очищенное имя файла
    """
    if not filename:
        return ""

    # Транслитерируем русские символы
    transliterated = transliterate_russian_to_english(filename)

    # Заменяем пробелы на подчеркивания
    no_spaces = transliterated.replace(' ', '_')

    # Удаляем недопустимые символы для имен файлов
    # Оставляем только буквы, цифры, точки, дефисы и подчеркивания
    sanitized = re.sub(r'[^\w\.\-_]', '', no_spaces)

    # Убираем множественные подчеркивания
    sanitized = re.sub(r'_+', '_', sanitized)

    # Убираем подчеркивания в начале и конце
    sanitized = sanitized.strip('_')

    # Если имя файла стало пустым, используем fallback
    if not sanitized:
        sanitized = "file"

    return sanitized

def get_safe_filename(original_filename: str) -> str:
    """
    Получает безопасное имя файла с сохранением расширения

    Args:
        original_filename: Исходное имя файла

    Returns:
        str: Безопасное имя файла
    """
    if not original_filename:
        return "file"

    # Разделяем имя файла и расширение
    if '.' in original_filename:
        name, extension = original_filename.rsplit('.', 1)
        safe_name = sanitize_filename(name)
        safe_extension = sanitize_filename(extension)
        return f"{safe_name}.{safe_extension}"
    else:
        return sanitize_filename(original_filename)
