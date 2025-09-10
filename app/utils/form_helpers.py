
import logging
from typing import Any, Dict, Optional, Union

from flask import current_app, flash, redirect, request, url_for
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def get_form_data(field_name: str, default: str = "") -> str:
    return request.form.get(field_name, default).strip()

def get_file_from_form(field_name: str):
    return request.files.get(field_name)

def handle_form_submission(
    form_name: str,
    success_message: str,
    error_message: str,
    redirect_endpoint: str,
    **redirect_kwargs
) -> Optional[Union[str, redirect]]:
    if request.method == "POST" and request.form.get("submit") == form_name:
        try:
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
    if not current_user.is_authenticated:
        flash("Необходима авторизация", "error")
        return False

    if required_admin and not current_user.is_admin:
        flash("Недостаточно прав", "error")
        return False

    return True

def safe_int_conversion(value: str, field_name: str = "field") -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Invalid integer value for {field_name}: {value}")
        flash(f"Некорректное значение для {field_name}", "error")
        return None

def log_form_action(action: str, user_id: Optional[int] = None, **kwargs) -> None:
    user_id = user_id or (current_user.id if current_user.is_authenticated else None)
    logger.info(f"Form action: {action}, user_id: {user_id}, params: {kwargs}")

def handle_database_operation(operation_func, success_message: str, error_message: str):
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
