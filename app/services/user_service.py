import secrets
import string
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from flask import current_app
from werkzeug.security import generate_password_hash
from .. import db
from ..models import (
    ChatMessage,
    EmailVerification,
    Group,
    Notification,
    Payment,
    SiteSettings,
    Submission,
    Ticket,
    TicketMessage,
    User,
)
from ..utils.file_storage import FileStorageManager


class UserService:
    """Сервис для управления пользователями"""

    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        is_admin: bool = False,
        is_moderator: bool = False,
        group_id: Optional[int] = None,
    ) -> Tuple[Optional[User], str]:
        """Создание нового пользователя"""
        try:
            existing = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            if existing:
                if existing.username == username:
                    return None, f'Пользователь с именем "{username}" уже существует'
                else:
                    return None, f'Пользователь с email "{email}" уже существует'
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=is_admin,
                is_moderator=is_moderator,
                is_subscribed=False,
                group_id=group_id,
            )
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(
                f"Пользователь {username} успешно создан с ID: {user.id}"
            )
            return user, f"Пользователь {username} успешно создан"
        except Exception as e:
            current_app.logger.error(f"Ошибка создания пользователя {username}: {e}")
            db.session.rollback()
            return None, "Ошибка при создании пользователя"

    @staticmethod
    def update_user(
        user_id: int, username: Optional[str] = None, email: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Обновление данных пользователя"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Пользователь не найден"
            if username:
                existing = User.query.filter(
                    User.username == username, User.id != user_id
                ).first()
                if existing:
                    return False, f'Пользователь с именем "{username}" уже существует'
                user.username = username
            if email:
                existing = User.query.filter(
                    User.email == email, User.id != user_id
                ).first()
                if existing:
                    return False, f'Пользователь с email "{email}" уже существует'
                user.email = email
            db.session.commit()
            if username:
                current_app.logger.info(f"Пользователю {user.username} изменено имя на '{username}'")
            if email:
                current_app.logger.info(f"Пользователю {user.username} изменен email на '{email}'")
            return True, f"Пользователь успешно обновлен"
        except Exception as e:
            current_app.logger.error(f"Ошибка обновления пользователя {user_id}: {e}")
            db.session.rollback()
            return False, "Ошибка при обновлении пользователя"

    @staticmethod
    def delete_user(user_id: int, current_user_id: int) -> Tuple[bool, str]:
        """Удаление пользователя с проверками"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Пользователь не найден"
            if user.id == current_user_id:
                return False, "Нельзя удалить самого себя"
            if user.is_admin:
                return False, "Нельзя удалить администратора"
            UserService._delete_user_related_data(user_id, user.username)
            if not FileStorageManager.delete_user_files(user_id):
                current_app.logger.warning(
                    f"Ошибка удаления файлов пользователя {user_id}"
                )
            db.session.delete(user)
            db.session.commit()
            current_app.logger.info(f"Пользователь {user.username} успешно удален")
            return True, f"Пользователь {user.username} успешно удален"
        except Exception as e:
            current_app.logger.error(f"Ошибка удаления пользователя {user_id}: {e}")
            db.session.rollback()
            return False, "Ошибка при удалении пользователя"

    @staticmethod
    def _delete_user_related_data(user_id: int, username: str) -> None:
        """Удаление связанных с пользователем данных"""
        try:
            notifications_count = Notification.query.filter_by(user_id=user_id).delete()
            current_app.logger.info(
                f"Удалено уведомлений пользователя {username}: {notifications_count}"
            )
            ticket_messages_count = TicketMessage.query.filter_by(
                user_id=user_id
            ).delete()
            current_app.logger.info(
                f"Удалено сообщений тикетов пользователя {username}: {ticket_messages_count}"
            )
            tickets_count = Ticket.query.filter_by(user_id=user_id).delete()
            current_app.logger.info(
                f"Удалено тикетов пользователя {username}: {tickets_count}"
            )
            email_verifications_count = EmailVerification.query.filter_by(
                user_id=user_id
            ).delete()
            current_app.logger.info(
                f"Удалено кодов подтверждения email пользователя {username}: {email_verifications_count}"
            )
            payments_count = Payment.query.filter_by(user_id=user_id).delete()
            current_app.logger.info(
                f"Удалено платежей пользователя {username}: {payments_count}"
            )
            submissions_count = (
                db.session.query(Submission).filter_by(user_id=user_id).count()
            )
            db.session.query(Submission).filter_by(user_id=user_id).delete()
            current_app.logger.info(
                f"Удалено решений пользователя {username}: {submissions_count}"
            )
            chat_messages_count = ChatMessage.query.filter_by(user_id=user_id).delete()
            current_app.logger.info(
                f"Удалено сообщений чата пользователя {username}: {chat_messages_count}"
            )
        except Exception as e:
            current_app.logger.error(
                f"Ошибка удаления связанных данных пользователя {username}: {e}"
            )

    @staticmethod
    def reset_user_password(user_id: int) -> Tuple[Optional[str], str]:
        """Сброс пароля пользователя"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "Пользователь не найден"
            new_password = "".join(
                secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*_")
            )
            user.password = generate_password_hash(new_password)
            db.session.commit()
            current_app.logger.info(
                f"Пароль пользователя {user.username} успешно сброшен"
            )
            return new_password, f"Пароль пользователя {user.username} успешно сброшен"
        except Exception as e:
            current_app.logger.error(
                f"Ошибка сброса пароля пользователя {user_id}: {e}"
            )
            db.session.rollback()
            return None, "Ошибка при сбросе пароля"

    @staticmethod
    def change_user_group(
        user_id: int, group_id: Optional[int], new_group_id: Optional[int]
    ) -> Tuple[bool, str]:
        """Изменение группы пользователя"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Пользователь не найден"
            if new_group_id:
                group = Group.query.get(new_group_id)
                if not group:
                    return False, "Группа не найдена"
                user.group_id = group.id
                db.session.commit()
                current_app.logger.info(
                    f"Пользователь {user.username} успешно перемещен в группу '{group.name}'"
                )
                return (
                    True,
                    f"Пользователь {user.username} перемещен в группу '{group.name}'",
                )
            else:
                user.group_id = None
                db.session.commit()
                current_app.logger.info(
                    f"Пользователь {user.username} успешно убран из группы"
                )
                return True, f"Пользователь {user.username} убран из группы"
        except Exception as e:
            current_app.logger.error(
                f"Ошибка изменения группы пользователя {user_id}: {e}"
            )
            db.session.rollback()
            return False, "Ошибка при изменении группы пользователя"

    @staticmethod
    def change_user_status(
        user_id: int,
        current_user_id: int,
        new_role: str,
        admin_mode_enabled: bool = False,
    ) -> Tuple[bool, str]:
        """Изменение статуса/роли пользователя"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Пользователь не найден"
            if user_id == current_user_id:
                return False, "Нельзя изменить статус администратора для самого себя"
            user.is_admin = False
            user.is_moderator = False
            user.admin_mode_enabled = False
            if new_role == "admin":
                user.is_admin = True
                user.admin_mode_enabled = admin_mode_enabled
                mode = "админ" if admin_mode_enabled else "пользователь"
                message = f"Пользователь {user.username} назначен администратором в режиме {mode}"
            elif new_role == "moderator":
                user.is_moderator = True
                message = f"Пользователь {user.username} назначен модератором"
            else:
                message = f"Пользователь {user.username} назначен обычным пользователем"
            db.session.commit()
            current_app.logger.info(message)
            return True, message
        except Exception as e:
            current_app.logger.error(
                f"Ошибка изменения статуса пользователя {user_id}: {e}"
            )
            db.session.rollback()
            return False, "Ошибка при изменении статуса пользователя"

    @staticmethod
    def toggle_admin_mode(user_id: int) -> Tuple[bool, str]:
        """Переключение режима администратора"""
        try:
            user = User.query.get(user_id)
            if not user or not user.is_admin:
                return False, "Недостаточно прав"
            user.admin_mode_enabled = not user.admin_mode_enabled
            mode = "админ" if user.admin_mode_enabled else "пользователь"
            db.session.commit()
            current_app.logger.info(f"Пользователь {user.username} переключен в режим {mode}")
            return True, f"Переключен в режим {mode}"
        except Exception as e:
            current_app.logger.error(
                f"Ошибка переключения режима админа {user_id}: {e}"
            )
            db.session.rollback()
            return False, "Ошибка при переключении режима"

    @staticmethod
    def toggle_subscription(user_id: int) -> Tuple[bool, str]:
        """Переключение подписки пользователя"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Пользователь не найден"
            if user.is_subscribed:
                user.is_subscribed = False
                user.subscription_expires = None
                user.is_manual_subscription = False
                status = "отозвана"
            else:
                trial_days = int(
                    SiteSettings.get_setting("trial_subscription_days", 14)
                )
                user.is_subscribed = True
                user.subscription_expires = datetime.utcnow() + timedelta(
                    days=trial_days
                )
                user.is_manual_subscription = True
                status = f"выдана на {trial_days} дней"
            db.session.commit()
            current_app.logger.info(f"Подписка для пользователя {user.username} {status}")
            return True, f"Подписка для пользователя {user.username} {status}"
        except Exception as e:
            current_app.logger.error(
                f"Ошибка изменения подписки пользователя {user_id}: {e}"
            )
            db.session.rollback()
            return False, "Ошибка при изменении подписки"

    @staticmethod
    def mass_delete_users(user_ids: List[int], current_user_id: int) -> Tuple[int, str]:
        """Массовое удаление пользователей"""
        try:
            deleted_count = 0
            for user_id in user_ids:
                user = User.query.get(user_id)
                if user and user.id != current_user_id and not user.is_admin:
                    UserService._delete_user_related_data(user_id, user.username)
                    if not FileStorageManager.delete_user_files(user_id):
                        current_app.logger.warning(
                            f"Ошибка удаления файлов пользователя {user_id}"
                        )
                    db.session.delete(user)
                    deleted_count += 1
            db.session.commit()
            message = f"Удалено {deleted_count} пользователей"
            current_app.logger.info(message)
            return deleted_count, message
        except Exception as e:
            current_app.logger.error(f"Ошибка массового удаления пользователей: {e}")
            db.session.rollback()
            return 0, "Ошибка при массовом удалении пользователей"

    @staticmethod
    def mass_change_group(
        user_ids: List[int], group_id: Optional[int], current_user_id: int
    ) -> Tuple[int, str]:
        """Массовое назначение группы"""
        try:
            updated_count = 0
            for user_id in user_ids:
                user = User.query.get(user_id)
                if user and user.id != current_user_id:
                    user.group_id = group_id
                    updated_count += 1
            db.session.commit()
            if group_id:
                group = Group.query.get(group_id)
                group_name = group.name if group else "неизвестная"
                message = (
                    f"Группа '{group_name}' назначена {updated_count} пользователям"
                )
            else:
                message = f"Убрано из групп {updated_count} пользователей"
            current_app.logger.info(message)
            return updated_count, message
        except Exception as e:
            current_app.logger.error(f"Ошибка массового назначения группы: {e}")
            db.session.rollback()
            return 0, "Ошибка при массовом назначении группы"

    @staticmethod
    def mass_change_status(
        user_ids: List[int], status: str, current_user_id: int
    ) -> Tuple[int, str]:
        """Массовое изменение статуса"""
        try:
            updated_count = 0
            for user_id in user_ids:
                user = User.query.get(user_id)
                if user and user.id != current_user_id:
                    user.is_admin = False
                    user.is_moderator = False
                    user.admin_mode_enabled = False
                    if status == "admin":
                        user.is_admin = True
                    elif status == "moderator":
                        user.is_moderator = True
                    updated_count += 1
            db.session.commit()
            status_names = {
                "admin": "администратор",
                "moderator": "модератор",
                "user": "пользователь",
            }
            status_name = status_names.get(status, "пользователь")
            message = f"Статус '{status_name}' назначен {updated_count} пользователям"
            current_app.logger.info(message)
            return updated_count, message
        except Exception as e:
            current_app.logger.error(f"Ошибка массового изменения статуса: {e}")
            db.session.rollback()
            return 0, "Ошибка при массовом изменении статуса"
