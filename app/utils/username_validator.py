import re
from typing import List

FORBIDDEN_WORDS = [
    "никита",
    "вагнер",
    "cysu",
    "cy7su",
    "admin",
    "administrator",
    "root",
    "moderator",
    "mod",
    "support",
    "bot",
    "test",
    "demo",
    "user",
    "guest",
    "fuck",
    "shit",
    "penis",
    "pussy",
    "sex",
    "naked",
    "porn",
    "xxx",
    "bitch",
    "nigger",
    "faggot",
    "asshole",
    "bastard",
    "cunt",
    "dick",
    "motherfucker",
    "whore",
    "slut",
    "tits",
    "cum",
    "ejackulate",
    "orgasm",
    "fap",
    "wank",
    "jerk",
    "jizz",
    "sperm",
    "rape",
    "pedo",
    "cuck",
    "milf",
    "hentai",
    "necrophilia",
    "incest",
    "gangbang",
    "bdsm",
    "hitler",
    "nazi",
    "isis",
    "alqaeda",
    "terrorist",
    "mumford",
    "mothafucka",
    "nigga",
    "lobster",
    "lobzta",
    "kike",
    "coon",
    "jewboy",
    "wetback",
    "spic",
    "chink",
    "gook",
    "sandnigger",
    "cameljockey",
    "paki",
    "gypsy",
    "redskin",
    "squaw",
    "eskimo",
    "injun",
    "wop",
    "dago",
    "kraut",
    "frog",
    "limey",
    "paddy",
    "taig",
    "hajji",
    "infidel",
    "kaffir",
    "coolie",
    "filipino",
    "vietcong",
    "zipperhead",
    "archie",
    "buffalo",
    "sket",
    "wigger",
    "cracker",
    "hillbilly",
    "trailertrash",
    "redneck",
    "system",
]
CHAR_REPLACEMENTS = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "@": "a",
    "$": "s",
    "!": "i",
    "|": "i",
    "l": "i",
    "к": "k",
    "в": "b",
    "а": "a",
    "г": "g",
    "н": "n",
    "е": "e",
    "р": "r",
    "и": "i",
    "т": "t",
}
USERNAME_ALLOWED_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё0-9_]+$")


def has_allowed_characters(username: str) -> bool:
    if not username:
        return False

    if len(username) < 2 or len(username) > 14:
        return False
    return bool(USERNAME_ALLOWED_PATTERN.fullmatch(username))


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
        "a": "[a@4а]",
        "b": "[b8в]",
        "c": "[c(с]",
        "e": "[e3е]",
        "g": "[g9г]",
        "i": "[i1l|!и]",
        "k": "[kк]",
        "n": "[nн]",
        "o": "[o0о]",
        "r": "[rр]",
        "s": "[s5$]",
        "t": "[t7т]",
        "u": "[uу]",
        "y": "[yу]",
        "z": "[z2]",
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
    username_variants = [username_lower, normalized]
    for forbidden_word in FORBIDDEN_WORDS:
        base = forbidden_word.lower()
        normalized_base = normalize_username(base)
        forbidden_variants = {
            base,
            normalized_base,
            base[::-1],
            normalized_base[::-1],
        }
        for username_variant in username_variants:
            for forbidden_variant in forbidden_variants:
                if forbidden_variant and forbidden_variant in username_variant:
                    return True
                pattern = create_fuzzy_pattern(forbidden_variant)
                if re.search(pattern, username_variant, re.IGNORECASE):
                    return True
    return False


def get_forbidden_words_list() -> List[str]:
    return FORBIDDEN_WORDS.copy()


def validate_username_length(username: str) -> bool:
    """
    Проверяет допустимую длину username.
    Поскольку WTForms имеет встроенную проверку длины,
    эта функция нужна для обратной совместимости.
    """
    if not username:
        return False
    return 3 <= len(username) <= 14
