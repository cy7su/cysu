"""
Context processors для всех blueprint'ов
"""

from flask import current_app
from flask_login import current_user
from typing import Dict, Any
import json
import locale
from datetime import datetime
from time import time

from ..models import User, SiteSettings
from ..utils.payment_service import YooKassaService


def inject_json_parser() -> Dict[str, Any]:
    """Добавляет функцию для парсинга JSON в шаблоны"""
    def parse_json(json_string: str) -> list:
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return []

    return dict(parse_json=parse_json)


def inject_timestamp() -> Dict[str, int]:
    """Добавляет timestamp для предотвращения кэширования CSS/JS"""
    return dict(timestamp=int(time()))


def inject_moment() -> Dict[str, Any]:
    """Добавляет функцию moment для форматирования дат"""
    # Устанавливаем русскую локаль для дат
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    except (locale.Error, OSError):
        try:
            locale.setlocale(locale.LC_TIME, 'ru_RU')
        except (locale.Error, OSError):
            pass  # Если русская локаль недоступна, используем системную
    
    def moment() -> datetime:
        return datetime.now()
    
    def format_date_russian() -> str:
        """Форматирует дату на русском языке с fallback"""
        now = datetime.now()
        try:
            return now.strftime('%d %B %Y')
        except (ValueError, OSError):
            # Fallback на английский формат
            months_en = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']
            return f"{now.day} {months_en[now.month-1]} {now.year}"
    
    return dict(moment=moment, format_date_russian=format_date_russian)


def inject_admin_users() -> Dict[str, Any]:
    """
    Context processor для передачи списка пользователей в шаблоны.
    """
    try:
        users = (
            User.query.all()
            if current_user.is_authenticated and current_user.is_admin
            else []
        )
    except Exception as e:
        current_app.logger.error(f"Error in inject_admin_users: {e}")
        users = []
    return dict(users=users)


def inject_subscription_status() -> Dict[str, Any]:
    """
    Context processor для передачи актуального статуса подписки в шаблоны.
    """
    is_subscribed = False
    trial_info = None
    
    if current_user.is_authenticated:
        try:
            current_app.logger.info(f"Проверяем подписку для пользователя: {current_user.username}")
            current_app.logger.info(f"is_trial_subscription: {current_user.is_trial_subscription}")
            current_app.logger.info(f"trial_subscription_expires: {current_user.trial_subscription_expires}")
            
            payment_service = YooKassaService()
            is_subscribed = payment_service.check_user_subscription(current_user)
            
            # Получаем информацию о пробной подписке
            if current_user.is_trial_subscription:
                trial_info = payment_service.get_trial_subscription_info(current_user)
                current_app.logger.info(f"Получена информация о пробной подписке: {trial_info}")
            else:
                current_app.logger.info("Пользователь не имеет пробной подписки")
                
        except Exception as e:
            current_app.logger.error(f"Error in inject_subscription_status: {e}")
            is_subscribed = False
            trial_info = None
    else:
        current_app.logger.info("Пользователь не авторизован")
            
    return dict(is_subscribed=is_subscribed, trial_info=trial_info)


def inject_maintenance_mode() -> Dict[str, Any]:
    """Добавляет информацию о режиме технических работ в шаблоны"""
    try:
        maintenance_mode = SiteSettings.get_setting('maintenance_mode', False)
        return dict(maintenance_mode=maintenance_mode)
    except Exception as e:
        current_app.logger.error(f'Error in inject_maintenance_mode: {e}')
        return dict(maintenance_mode=False)
