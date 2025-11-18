import json
import locale
from datetime import datetime
from typing import Any, Dict

from flask import current_app
from flask_login import current_user

from ..models import SiteSettings, User
from ..services import UserManagementService
from ..utils.payment_service import YooKassaService


def inject_json_parser() -> Dict[str, Any]:
    def parse_json(json_string: str) -> list:
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return []

    return dict(parse_json=parse_json)


def inject_timestamp() -> Dict[str, int]:
    return dict(timestamp=4)


def inject_moment() -> Dict[str, Any]:
    try:
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    except (locale.Error, OSError):
        try:
            locale.setlocale(locale.LC_TIME, "ru_RU")
        except (locale.Error, OSError):
            pass

    def moment() -> datetime:
        return datetime.now()

    def format_date_russian() -> str:
        now = datetime.now()
        try:
            return now.strftime("%d %B %Y")
        except (ValueError, OSError):
            months_en = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            return f"{now.day} {months_en[now.month-1]} {now.year}"

    return dict(moment=moment, format_date_russian=format_date_russian)


def inject_admin_users() -> Dict[str, Any]:
    try:
        users = (
            User.query.all()
            if current_user.is_authenticated
            and UserManagementService.is_effective_admin(current_user)
            else []
        )
    except Exception as e:
        current_app.logger.error(f"Error in inject_admin_users: {e}")
        users = []
    return dict(users=users)


def inject_subscription_status() -> Dict[str, Any]:
    is_subscribed = False
    subscription_info = None
    if current_user.is_authenticated:
        try:
            current_app.logger.info(f"Проверяем подписку для пользователя: {current_user.username}")
            current_app.logger.info(f"is_trial_subscription: {current_user.is_trial_subscription}")
            current_app.logger.info(
                f"trial_subscription_expires: {current_user.trial_subscription_expires}"
            )
            payment_service = YooKassaService()
            is_subscribed = UserManagementService.has_active_subscription(current_user)
            subscription_info = payment_service.get_subscription_info(current_user)
            current_app.logger.info(f"Получена информация о подписке: {subscription_info}")
        except Exception as e:
            current_app.logger.error(f"Error in inject_subscription_status: {e}")
            is_subscribed = False
            subscription_info = None
    else:
        current_app.logger.info("Пользователь не авторизован")
    return dict(is_subscribed=is_subscribed, subscription_info=subscription_info)


def inject_maintenance_mode() -> Dict[str, Any]:
    try:
        maintenance_mode = SiteSettings.get_setting("maintenance_mode", False)
        return dict(maintenance_mode=maintenance_mode)
    except Exception as e:
        current_app.logger.error(f"Error in inject_maintenance_mode: {e}")
        return dict(maintenance_mode=False)


def inject_support_enabled() -> Dict[str, Any]:
    try:
        support_enabled = SiteSettings.get_setting("support_enabled", True)
        return dict(support_enabled=support_enabled)
    except Exception as e:
        current_app.logger.error(f"Error in inject_support_enabled: {e}")
        return dict(support_enabled=True)
