import os
import shutil
from datetime import datetime
from typing import List, Tuple

from flask import current_app

from .transliteration import get_safe_filename


def safe_path_join(base_path: str, *path_parts: str) -> str:
    """
    Безопасное соединение путей, предотвращающее Path Traversal атаки

    Args:
        base_path: Базовый путь
        *path_parts: Части пути для соединения

    Returns:
        str: Безопасный абсолютный путь
    """
    # Нормализуем базовый путь
    base_path = os.path.abspath(base_path)

    # Соединяем все части пути
    full_path = os.path.join(base_path, *path_parts)

    # Нормализуем полный путь
    full_path = os.path.abspath(full_path)

    # Проверяем, что результирующий путь находится внутри базового пути
    if not full_path.startswith(base_path):
        raise ValueError(
            f"Path traversal detected: {full_path} is outside {base_path}"
        )

    return full_path


class FileStorageManager:

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "txt", "rtf", "odt"}
    ALLOWED_ARCHIVE_EXTENSIONS = {"zip", "rar", "7z", "tar", "gz"}
    ALLOWED_TICKET_EXTENSIONS = (
        ALLOWED_IMAGE_EXTENSIONS
        | ALLOWED_DOCUMENT_EXTENSIONS
        | ALLOWED_ARCHIVE_EXTENSIONS
    )

    MAX_FILE_SIZE = 200 * 1024 * 1024  # 50MB
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB для изображений

    @staticmethod
    def get_subject_upload_path(
        subject_id: int, user_id: int, filename: str
    ) -> Tuple[str, str]:
        safe_filename = get_safe_filename(filename)

        upload_base = current_app.config.get(
            "UPLOAD_FOLDER", "app/static/uploads"
        )
        subject_path = os.path.join(upload_base, str(subject_id))
        users_path = os.path.join(subject_path, "users")
        user_path = os.path.join(users_path, str(user_id))

        os.makedirs(user_path, exist_ok=True)

        full_path = os.path.join(user_path, safe_filename)

        relative_path = os.path.join(
            str(subject_id), "users", str(user_id), safe_filename
        )

        return full_path, relative_path

    @staticmethod
    def get_material_upload_path(
        subject_id: int, filename: str
    ) -> Tuple[str, str]:
        safe_filename = get_safe_filename(filename)

        upload_base = current_app.config.get(
            "UPLOAD_FOLDER", "app/static/uploads"
        )
        subject_path = os.path.join(upload_base, str(subject_id))

        os.makedirs(subject_path, exist_ok=True)

        full_path = os.path.join(subject_path, safe_filename)

        relative_path = os.path.join(str(subject_id), safe_filename)

        return full_path, relative_path

    @staticmethod
    def get_chat_file_path(user_id: int, filename: str) -> Tuple[str, str]:
        chat_base = current_app.config.get(
            "CHAT_FILES_FOLDER", "app/static/chat_files"
        )
        user_path = os.path.join(chat_base, str(user_id))

        os.makedirs(user_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_filename = get_safe_filename(filename)
        name, ext = os.path.splitext(safe_filename)
        unique_filename = f"{timestamp}_{name}{ext}"

        full_path = os.path.join(user_path, unique_filename)

        relative_path = os.path.join(str(user_id), unique_filename)

        return full_path, relative_path

    @staticmethod
    def get_ticket_file_path(ticket_id: int, filename: str) -> Tuple[str, str]:
        ticket_base = current_app.config.get(
            "TICKET_FILES_FOLDER", "app/static/ticket_files"
        )

        # Безопасное создание пути
        try:
            ticket_path = safe_path_join(ticket_base, str(ticket_id))
        except ValueError as e:
            current_app.logger.error(f"Path traversal attempt detected: {e}")
            raise ValueError("Invalid path")

        os.makedirs(ticket_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_filename = get_safe_filename(filename)
        name, ext = os.path.splitext(safe_filename)
        unique_filename = f"{timestamp}_{name}{ext}"

        # Безопасное создание полного пути
        try:
            full_path = safe_path_join(ticket_path, unique_filename)
        except ValueError as e:
            current_app.logger.error(f"Path traversal attempt detected: {e}")
            raise ValueError("Invalid filename")

        relative_path = os.path.join(str(ticket_id), unique_filename)

        return full_path, relative_path

    @staticmethod
    def save_file(file, full_path: str) -> bool:
        try:
            # Проверяем, что путь безопасен
            try:
                safe_full_path = safe_path_join(
                    os.path.dirname(full_path), os.path.basename(full_path)
                )
            except ValueError as e:
                current_app.logger.error(
                    f"Path traversal attempt detected: {e}"
                )
                return False

            file_size = getattr(file, "content_length", None)
            file_name = getattr(file, "filename", "unknown")

            current_app.logger.info(
                f"Попытка сохранения файла: {safe_full_path}"
            )
            current_app.logger.info(f"Исходное имя файла: {file_name}")
            current_app.logger.info(
                f"Размер файла: {file_size} байт ({file_size / (1024*1024):.2f} MB)"
                if file_size
                else "Размер файла: неизвестен"
            )
            current_app.logger.info(
                f"Папка назначения: {os.path.dirname(safe_full_path)}"
            )
            current_app.logger.info(
                f"Папка существует: {os.path.exists(os.path.dirname(safe_full_path))}"
            )

            try:
                statvfs = os.statvfs(os.path.dirname(safe_full_path))
                free_space = statvfs.f_frsize * statvfs.f_bavail
                current_app.logger.info(
                    f"Свободное место на диске: {free_space} байт ({free_space / (1024*1024):.2f} MB)"
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Не удалось получить информацию о свободном месте: {e}"
                )

            file.save(safe_full_path)

            if os.path.exists(safe_full_path):
                saved_size = os.path.getsize(safe_full_path)
                current_app.logger.info(
                    f"Файл успешно сохранен: {safe_full_path}"
                )
                current_app.logger.info(
                    f"Размер сохраненного файла: {saved_size} байт ({saved_size / (1024*1024):.2f} MB)"
                )

                if file_size and saved_size != file_size:
                    current_app.logger.warning(
                        f"Размеры не совпадают! Ожидалось: {file_size}, получено: {saved_size}"
                    )
            else:
                current_app.logger.error(
                    f"Файл не найден после сохранения: {safe_full_path}"
                )
                return False

            return True
        except Exception as e:
            current_app.logger.error(
                f"Ошибка сохранения файла {full_path}: {str(e)}"
            )
            import traceback

            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def delete_file(relative_path: str) -> bool:
        try:
            static_folder = current_app.static_folder
            full_path = os.path.join(static_folder, relative_path)

            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(
                f"Ошибка удаления файла {relative_path}: {str(e)}"
            )
            return False

    @staticmethod
    def delete_ticket_files(ticket_id: int) -> bool:
        try:
            ticket_base = current_app.config.get(
                "TICKET_FILES_FOLDER", "app/static/ticket_files"
            )
            ticket_path = os.path.join(ticket_base, str(ticket_id))

            if os.path.exists(ticket_path):
                shutil.rmtree(ticket_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(
                f"Ошибка удаления файлов тикета {ticket_id}: {str(e)}"
            )
            return False

    @staticmethod
    def delete_user_files(user_id: int) -> bool:
        try:
            chat_base = current_app.config.get(
                "CHAT_FILES_FOLDER", "app/static/chat_files"
            )
            chat_path = os.path.join(chat_base, str(user_id))
            if os.path.exists(chat_path):
                shutil.rmtree(chat_path)

            upload_base = current_app.config.get(
                "UPLOAD_FOLDER", "app/static/uploads"
            )
            if os.path.exists(upload_base):
                for subject_folder in os.listdir(upload_base):
                    subject_path = os.path.join(upload_base, subject_folder)
                    if os.path.isdir(subject_path):
                        users_path = os.path.join(subject_path, "users")
                        if os.path.exists(users_path):
                            user_path = os.path.join(users_path, str(user_id))
                            if os.path.exists(user_path):
                                shutil.rmtree(user_path)

            return True
        except Exception as e:
            current_app.logger.error(
                f"Ошибка удаления файлов пользователя {user_id}: {str(e)}"
            )
            return False

    @staticmethod
    def get_file_type(filename: str) -> str:
        if not filename or "." not in filename:
            return "unknown"

        extension = filename.rsplit(".", 1)[1].lower()

        if extension in FileStorageManager.ALLOWED_IMAGE_EXTENSIONS:
            return "image"
        elif extension in FileStorageManager.ALLOWED_DOCUMENT_EXTENSIONS:
            return "document"
        elif extension in FileStorageManager.ALLOWED_ARCHIVE_EXTENSIONS:
            return "archive"
        else:
            return "unknown"

    @staticmethod
    def is_allowed_file(filename: str, allowed_extensions: set = None) -> bool:
        if not filename or "." not in filename:
            return False

        if allowed_extensions is None:
            allowed_extensions = FileStorageManager.ALLOWED_TICKET_EXTENSIONS

        extension = filename.rsplit(".", 1)[1].lower()
        return extension in allowed_extensions

    @staticmethod
    def validate_file_size(file, max_size: int = None) -> bool:
        if max_size is None:
            max_size = FileStorageManager.MAX_FILE_SIZE

        file_size = FileStorageManager.get_file_size(file)
        return file_size <= max_size

    @staticmethod
    def get_file_size(file) -> int:
        try:
            current_pos = file.tell()

            file.seek(0, 2)
            size = file.tell()

            file.seek(current_pos)

            return size
        except Exception:
            return 0

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    @staticmethod
    def process_ticket_files(files: List, ticket_id: int) -> List[dict]:
        saved_files = []

        for file in files:
            if not file or not file.filename or not file.filename.strip():
                continue

            if not FileStorageManager.validate_file_size(file):
                current_app.logger.warning(
                    f"Файл {file.filename} слишком большой"
                )
                continue

            if not FileStorageManager.is_allowed_file(file.filename):
                current_app.logger.warning(
                    f"Неподдерживаемый тип файла: {file.filename}"
                )
                continue

            full_path, relative_path = FileStorageManager.get_ticket_file_path(
                ticket_id, file.filename
            )

            if FileStorageManager.save_file(file, full_path):
                file_info = {
                    "file_path": relative_path,
                    "file_name": file.filename,
                    "file_size": FileStorageManager.get_file_size(file),
                    "file_type": FileStorageManager.get_file_type(
                        file.filename
                    ),
                }
                saved_files.append(file_info)
                current_app.logger.info(
                    f"Файл {file.filename} сохранен для тикета {ticket_id}"
                )
            else:
                current_app.logger.error(
                    f"Ошибка сохранения файла {file.filename}"
                )

        return saved_files
