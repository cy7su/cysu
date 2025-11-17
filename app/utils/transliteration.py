import re


def transliterate_russian_to_english(text: str) -> str:
    if not text:
        return ""
    transliteration_map = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "yo",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "j",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "Yo",
        "Ж": "Zh",
        "З": "Z",
        "И": "I",
        "Й": "J",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "Kh",
        "Ц": "Ts",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Sch",
        "Ъ": "",
        "Ы": "Y",
        "Ь": "",
        "Э": "E",
        "Ю": "Yu",
        "Я": "Ya",
    }
    result = ""
    for char in text:
        if char in transliteration_map:
            result += transliteration_map[char]
        else:
            result += char
    return result


def sanitize_filename(filename: str) -> str:
    if not filename:
        return ""
    transliterated = transliterate_russian_to_english(filename)
    no_spaces = transliterated.replace(" ", "_")
    sanitized = re.sub(r"[^\w\.\-_]", "", no_spaces)
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip("_")
    if not sanitized:
        sanitized = "file"
    return sanitized


def get_safe_filename(original_filename: str) -> str:
    if not original_filename:
        return "file"
    if "." in original_filename:
        name, extension = original_filename.rsplit(".", 1)
        safe_name = sanitize_filename(name)
        safe_extension = sanitize_filename(extension)
        return f"{safe_name}.{safe_extension}"
    else:
        return sanitize_filename(original_filename)
