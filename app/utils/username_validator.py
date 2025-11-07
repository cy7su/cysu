import re
from typing import List


# Список запрещенных слов (в нижнем регистре)
FORBIDDEN_WORDS = [
    "никита",
    "вагнер",
    "cysu",
    "cy7su",
]


# Маппинг похожих символов для нормализации
CHAR_REPLACEMENTS = {
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '7': 't',
    '8': 'b',
    '@': 'a',
    '$': 's',
    '!': 'i',
    '|': 'i',
    'l': 'i',  # маленькая L может быть похожа на i
    'к': 'k',
    'в': 'b',
    'а': 'a',
    'г': 'g',
    'н': 'n',
    'е': 'e',
    'р': 'r',
    'и': 'i',
    'т': 't',
}


def normalize_username(username: str) -> str:

    if not username:
        return ""

    username_lower = username.lower()

    normalized = ""
    for char in username_lower:
        if char in CHAR_REPLACEMENTS:
            normalized += CHAR_REPLACEMENTS[char]
        else:
            normalized += char

    return normalized


def create_fuzzy_pattern(word: str) -> str:
    char_patterns = {
        'a': '[a@4а]',
        'b': '[b8в]',
        'c': '[c(с]',
        'e': '[e3е]',
        'g': '[g9г]',
        'i': '[i1l|!и]',
        'k': '[kк]',
        'n': '[nн]',
        'o': '[o0о]',
        'r': '[rр]',
        's': '[s5$]',
        't': '[t7т]',
        'u': '[uу]',
        'y': '[yу]',
        'z': '[z2]',
    }

    pattern = ""
    for char in word.lower():
        if char in char_patterns:
            pattern += char_patterns[char]
        else:
            pattern += re.escape(char)

    return pattern


def contains_forbidden_word(username: str) -> bool:
    if not username:
        return False

    username_lower = username.lower()
    normalized = normalize_username(username_lower)

    # Проверяем каждое запрещенное слово
    for forbidden_word in FORBIDDEN_WORDS:
        # Прямое вхождение в оригинальном и нормализованном виде
        if forbidden_word in username_lower or forbidden_word in normalized:
            return True

        # Проверка с помощью регулярного выражения (учитывает замены символов)
        pattern = create_fuzzy_pattern(forbidden_word)
        if re.search(pattern, username_lower, re.IGNORECASE):
            return True

        # Также проверяем нормализованную версию
        normalized_pattern = create_fuzzy_pattern(normalize_username(forbidden_word))
        if re.search(normalized_pattern, normalized, re.IGNORECASE):
            return True

    return False


def get_forbidden_words_list() -> List[str]:
    return FORBIDDEN_WORDS.copy()

