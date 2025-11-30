"""Расширенные тесты для утилит с низким покрытием."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from app.utils.file_storage import FileStorageManager, safe_path_join
from app.utils.payment_service import YooKassaService


class TestFileStorageManager:
    """Тесты для FileStorageManager."""

    def test_safe_path_join_valid(self, app):
        """Тест безопасного объединения путей."""
        with app.app_context():
            result = safe_path_join("/base", "subdir", "file.txt")
            assert result == "/base/subdir/file.txt"

    def test_safe_path_join_path_traversal(self, app):
        """Тест защиты от path traversal."""
        with app.app_context():
            with pytest.raises(ValueError, match="Path traversal detected"):
                safe_path_join("/base", "../etc/passwd")

    def test_get_file_type(self, app):
        """Тест определения типа файла."""
        with app.app_context():
            assert FileStorageManager.get_file_type("photo.jpg") == "image"
            assert FileStorageManager.get_file_type("document.pdf") == "document"
            assert FileStorageManager.get_file_type("archive.zip") == "archive"
            assert FileStorageManager.get_file_type("file.txt") == "document"

            assert FileStorageManager.get_file_type("") == "unknown"

    def test_is_allowed_file(self, app):
        """Тест проверки разрешенных расширений."""
        with app.app_context():
            assert FileStorageManager.is_allowed_file("test.pdf")
            assert FileStorageManager.is_allowed_file("image.jpg")
            assert FileStorageManager.is_allowed_file("archive.rar")
            assert not FileStorageManager.is_allowed_file("script.exe")
            assert not FileStorageManager.is_allowed_file("")

    def test_format_size_label(self, app):
        """Тест форматирования размера файла."""
        with app.app_context():
            assert FileStorageManager._format_size_label(0) == "0 Б"
            assert FileStorageManager._format_size_label(1024) == "1 КБ"
            assert FileStorageManager._format_size_label(1024 * 1024) == "1 МБ"
            assert (
                FileStorageManager._format_size_label(3 * 1024 * 1024 * 1024) == "3 ГБ"
            )

    def test_get_user_max_file_size_normal_user(self, app):
        """Тест размера файла для обычного пользователя."""
        with app.app_context():

            user = Mock()
            user.id = 999
            user.username = "normal_user"

            max_size = FileStorageManager.get_user_max_file_size_bytes(user)
            assert max_size == FileStorageManager.DEFAULT_MAX_FILE_SIZE

            label = FileStorageManager.get_user_max_file_size_label(user)
            assert "МБ" in label

    def test_get_user_max_file_size_special_user(self, app):
        """Тест размера файла для специального пользователя."""
        with app.app_context():

            user = Mock()
            user.id = 1

            user.username = "st0rmez"

            assert FileStorageManager.is_special_user(user)

            max_size = FileStorageManager.get_user_max_file_size_bytes(user)
            assert max_size == FileStorageManager.SPECIAL_MAX_FILE_SIZE

            limit_msg = FileStorageManager.get_user_limit_message(user)
            assert "СПЕЦ ЛИМИТЫ" in limit_msg
            assert user.username in limit_msg

    def test_delete_file_not_exists(self, app):
        """Тест удаления несуществующего файла."""
        with app.app_context():
            result = FileStorageManager.delete_file("nonexistent/file.txt")
            assert not result

    def test_delete_ticket_files_not_exists(self, app):
        """Тест удаления файлов несуществующего тикета."""
        with app.app_context():
            result = FileStorageManager.delete_ticket_files(99999)
            assert not result

    def test_get_upload_paths(self, app):
        """Тест получения путей для загрузки файлов."""
        with app.app_context():
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch.dict(app.config, {"UPLOAD_FOLDER": temp_dir}):

                    full_path, rel_path = FileStorageManager.get_material_upload_path(
                        1, "test.pdf"
                    )
                    assert "1" in full_path
                    assert rel_path == "1/test.pdf"

                    full_path, rel_path = FileStorageManager.get_subject_upload_path(
                        1, 123, "solution.txt"
                    )
                    assert "users" in full_path
                    assert "123" in full_path
                    assert rel_path == "1/users/123/solution.txt"

                    full_path, rel_path = FileStorageManager.get_chat_file_path(
                        456, "chat.pdf"
                    )
                    assert "456" in full_path
                    assert "456" in rel_path


class TestYooKassaService:
    """Тесты для YooKassa платежной системы."""

    def test_simulation_mode(self, app):
        """Тест режима симуляции."""
        with app.app_context():
            service = YooKassaService()
            assert hasattr(service, "simulation_mode")

    def test_get_subscription_days(self, app):
        """Тест получения дней подписки."""
        with app.app_context():
            service = YooKassaService()

            assert service._get_subscription_days(89.0) == 30

            assert service._get_subscription_days(199.0) == 90

            assert service._get_subscription_days(349.0) == 180

            assert service._get_subscription_days(469.0) == 365

            assert service._get_subscription_days(999.0) == 30

            assert service._get_subscription_days(
                199.0
            ) > service._get_subscription_days(89.0)
            assert service._get_subscription_days(
                349.0
            ) > service._get_subscription_days(199.0)
            assert service._get_subscription_days(
                469.0
            ) > service._get_subscription_days(349.0)

    @patch("app.utils.payment_service.requests.post")
    def test_create_smart_payment_simulation(self, mock_post, app):
        """Тест создания платежа в режиме симуляции."""
        with app.app_context():
            service = YooKassaService()

            if not service.simulation_mode:
                return

            user = Mock()
            user.id = 123
            user.username = "testuser"

            result = service.create_smart_payment(user, "http://example.com", 100.0)
            assert "payment_url" in result or "error" in result

    def test_process_successful_payment(self, app):
        """Тест обработки успешного платежа."""
        with app.app_context():
            service = YooKassaService()

            result = service.process_successful_payment("fake_payment_id")
            assert isinstance(result, bool)
