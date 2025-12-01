"""Тесты для утилит."""

import pytest
from app.utils.file_storage import FileStorageManager
from app.utils.transliteration import get_safe_filename

try:
    from app.utils.email_validator import is_allowed_email_domain, validate_email_chars

    EMAIL_VALIDATOR_AVAILABLE = True
except ImportError:
    EMAIL_VALIDATOR_AVAILABLE = False


class TestEmailValidator:
    """Тесты для email валидации."""

    def test_valid_emails(self, app):
        """Тест валидных email адресов."""
        with app.app_context():
            assert is_allowed_email_domain("test@gmail.com")
            assert is_allowed_email_domain("user@yandex.ru")
            assert is_allowed_email_domain("user+tag@gmail.com")

    def test_invalid_emails(self, app):
        """Тест невалидных email адресов."""
        with app.app_context():
            assert not is_allowed_email_domain("")
            assert not is_allowed_email_domain("invalid")
            assert not is_allowed_email_domain("@domain.com")
            assert not is_allowed_email_domain("user@")

    def test_domain_check(self, app):
        """Тест проверки доменов."""
        with app.app_context():

            valid, msg = validate_email_chars("test@gmail.com")
            assert valid

            chars_valid, chars_msg = validate_email_chars("test@mailinator.com")
            assert chars_valid


class TestFileStorage:
    """Тесты для FileStorageManager."""

    def test_safe_filename(self, app):
        """Тест генерации безопасных имен файлов."""
        safe_name = get_safe_filename("test file.pdf")
        assert safe_name == "test_file.pdf"

        safe_name = get_safe_filename("test<file>.pdf")
        assert "<" not in safe_name
        assert ">" not in safe_name

    def test_file_operations(self, app):
        """Тест основных операций с файлами."""

        assert FileStorageManager is not None

        user_limit = FileStorageManager.get_user_limit_message(None)
        assert isinstance(user_limit, str)

        max_size = FileStorageManager.get_user_max_file_size_bytes(None)
        assert isinstance(max_size, int)
        assert max_size > 0


class TestTransliteration:
    """Тесты для транслитерации."""

    def test_cyrillic_transliteration(self, app):
        """Тест транслитерации кириллицы."""
        filename = get_safe_filename("тестовый файл.txt")
        assert "testovyj" in filename or "тестовый" not in filename

        assert " " not in filename

    def test_special_chars_replacement(self, app):
        """Тест замены специальных символов."""
        filename = get_safe_filename("file@#$%^&*().pdf")
        assert "@" not in filename
        assert "#" not in filename
        assert "$" not in filename
        assert "%" not in filename
        assert "^" not in filename
        assert "&" not in filename
        assert "*" not in filename
        assert "(" not in filename

        assert ")" not in filename
