"""
Утилиты для обработки форм (DRY принцип)
"""

from typing import Optional, Dict, Any, Union
from flask import request, flash, redirect, url_for, current_app
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def get_form_data(field_name: str, default: str = "") -> str:
    """
    Безопасно получает данные из формы

    Args:
        field_name: Имя поля формы
        default: Значение по умолчанию

    Returns:
        str: Значение поля или значение по умолчанию
    """
    return request.form.get(field_name, default).strip()

def get_file_from_form(field_name: str):
    """
    Безопасно получает файл из формы

    Args:
        field_name: Имя поля файла

    Returns:
        Файловый объект или None
    """
    return request.files.get(field_name)

def handle_form_submission(
    form_name: str,
    success_message: str,
    error_message: str,
    redirect_endpoint: str,
    **redirect_kwargs
) -> Optional[Union[str, redirect]]:
    """
    Обрабатывает отправку формы с общими проверками

    Args:
        form_name: Имя поля submit для проверки
        success_message: Сообщение об успехе
        error_message: Сообщение об ошибке
        redirect_endpoint: Эндпоинт для редиректа
        **redirect_kwargs: Параметры для редиректа

    Returns:
        redirect объект или None
    """
    if request.method == "POST" and request.form.get("submit") == form_name:
        try:
            # Здесь будет логика обработки формы
            # Каждая форма будет переопределять этот метод
            flash(success_message, "success")
            return redirect(url_for(redirect_endpoint, **redirect_kwargs))
        except SQLAlchemyError as e:
            logger.error(f"Database error in form submission: {e}")
            flash(error_message, "error")
        except Exception as e:
            logger.error(f"Unexpected error in form submission: {e}")
            flash("Произошла неожиданная ошибка", "error")

    return None

def validate_user_permissions(required_admin: bool = False) -> bool:
    """
    Проверяет права пользователя

    Args:
        required_admin: Требуется ли права администратора

    Returns:
        bool: True если права достаточны
    """
    if not current_user.is_authenticated:
        flash("Необходима авторизация", "error")
        return False

    if required_admin and not current_user.is_admin:
        flash("Недостаточно прав", "error")
        return False

    return True

def safe_int_conversion(value: str, field_name: str = "field") -> Optional[int]:
    """
    Безопасно конвертирует строку в int

    Args:
        value: Строковое значение
        field_name: Имя поля для логирования

    Returns:
        int или None при ошибке
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Invalid integer value for {field_name}: {value}")
        flash(f"Некорректное значение для {field_name}", "error")
        return None

def log_form_action(action: str, user_id: Optional[int] = None, **kwargs) -> None:
    """
    Логирует действия с формами

    Args:
        action: Действие
        user_id: ID пользователя
        **kwargs: Дополнительные параметры
    """
    user_id = user_id or (current_user.id if current_user.is_authenticated else None)
    logger.info(f"Form action: {action}, user_id: {user_id}, params: {kwargs}")

def handle_database_operation(operation_func, success_message: str, error_message: str):
    """
    Обрабатывает операции с базой данных

    Args:
        operation_func: Функция для выполнения
        success_message: Сообщение об успехе
        error_message: Сообщение об ошибке

    Returns:
        bool: True если операция успешна
    """
    try:
        operation_func()
        flash(success_message, "success")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        flash(error_message, "error")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        flash("Произошла неожиданная ошибка", "error")
        return False
