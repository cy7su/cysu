import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from .. import db
from ..models import Group, User, Subject, SubjectGroup


class UserManagementService:
    """Сервис для управления пользователями и их ролями"""

    @staticmethod
    def is_effective_admin(user: User) -> bool:
        """Проверяет, является ли пользователь эффективным администратором"""
        return user.is_admin and user.admin_mode_enabled

    @staticmethod
    def can_manage_materials(user: User) -> bool:
        """Проверяет, может ли пользователь управлять материалами"""
        return (user.is_admin and user.admin_mode_enabled) or user.is_moderator

    @staticmethod
    def can_see_all_subjects(user: User) -> bool:
        """Проверяет, может ли пользователь видеть все предметы"""
        return user.is_admin and user.admin_mode_enabled

    @staticmethod
    def get_accessible_subjects(user: User) -> List[Subject]:
        """Возвращает список доступных пользователю предметов"""
        if UserManagementService.can_see_all_subjects(user):
            return Subject.query.all()
        elif user.group_id:
            return (
                Subject.query.join(SubjectGroup)
                .filter(SubjectGroup.group_id == user.group_id)
                .all()
            )
        else:
            return []

    @staticmethod
    def can_add_materials_to_subject(user: User, subject: Subject) -> bool:
        """Проверяет, может ли пользователь добавлять материалы в предмет"""
        if user.is_admin and user.admin_mode_enabled:
            return True
        elif user.is_moderator and user.group_id:
            from ..models import SubjectGroup

            return (
                SubjectGroup.query.filter_by(
                    subject_id=subject.id, group_id=user.group_id
                ).first()
                is not None
            )
        else:
            return False

    @staticmethod
    def can_manage_subject_materials(user: User, subject: Subject) -> bool:
        """Проверяет, может ли пользователь управлять материалами предмета"""
        return UserManagementService.can_add_materials_to_subject(user, subject)

    @staticmethod
    def has_active_subscription(user: User) -> bool:
        """Проверяет, имеет ли пользователь активную подписку"""
        from .payment_service import PaymentService

        if (
            user.is_manual_subscription
            and user.subscription_expires
            and user.subscription_expires > datetime.utcnow()
        ):
            return True
        if (
            user.is_trial_subscription
            and user.trial_subscription_expires
            and user.trial_subscription_expires > datetime.utcnow()
        ):
            return True
        return (
            user.is_subscribed
            and user.subscription_expires
            and user.subscription_expires > datetime.utcnow()
        )

    @staticmethod
    def get_role_display(user: User) -> str:
        """Возвращает текстовое представление роли пользователя"""
        if user.is_admin:
            return "Администратор" + (
                " (Админ режим)" if user.admin_mode_enabled else " (Пользователь режим)"
            )
        elif user.is_moderator:
            return "Модератор"
        else:
            return "Пользователь"

    @staticmethod
    def toggle_admin_mode(user: User) -> bool:
        """Переключает режим администратора"""
        if not user.is_admin:
            return False
        user.admin_mode_enabled = not user.admin_mode_enabled
        db.session.commit()
        return user.admin_mode_enabled

    @staticmethod
    def grant_manual_subscription(user: User, days: int = 30) -> bool:
        """Выдает ручную подписку пользователю"""
        try:
            user.is_subscribed = True
            user.is_manual_subscription = True
            user.subscription_expires = datetime.utcnow() + timedelta(days=days)
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка выдачи ручной подписки: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def revoke_manual_subscription(user: User) -> bool:
        """Отзывает ручную подписку"""
        try:
            user.is_subscribed = False
            user.is_manual_subscription = False
            user.subscription_expires = None
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка отзыва подписки: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def grant_trial_subscription(user: User, days: int = 14) -> bool:
        """Выдает пробную подписку"""
        try:
            user.is_trial_subscription = True
            user.trial_subscription_expires = datetime.utcnow() + timedelta(days=days)
            user.is_subscribed = True
            user.subscription_expires = datetime.utcnow() + timedelta(days=days)
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка выдачи пробной подписки: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def change_user_group(user: User, group_id: int) -> bool:
        """Изменяет группу пользователя"""
        try:
            user.group_id = group_id
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка изменения группы: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def set_user_role(user: User, role: str) -> bool:
        """Устанавливает роль пользователя (admin, moderator, user)"""
        try:
            if role == "admin":
                user.is_admin = True
                user.is_moderator = False
            elif role == "moderator":
                user.is_admin = False
                user.is_moderator = True
            else:
                user.is_admin = False
                user.is_moderator = False
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка изменения роли: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def delete_user(user: User) -> bool:
        """Удаляет пользователя"""
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка удаления пользователя: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def get_users_count() -> int:
        """Возвращает количество пользователей"""
        return User.query.count()

    @staticmethod
    def get_users_count_by_role() -> Dict[str, int]:
        """Возвращает количество пользователей по ролям"""
        total = User.query.count()
        admins = User.query.filter_by(is_admin=True).count()
        moderators = User.query.filter_by(is_moderator=True).count()
        subscribed = User.query.filter_by(is_subscribed=True).count()
        return {
            "total": total,
            "admins": admins,
            "moderators": moderators,
            "users": total - admins - moderators,
            "subscribed": subscribed,
            "unsubscribed": total - subscribed,
        }

    @staticmethod
    def search_users(query: str, limit: int = 20) -> List[User]:
        """Ищет пользователей по username или email"""
        search_pattern = f"%{query}%"
        return (
            User.query.filter(
                db.or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )
            .limit(limit)
            .all()
        )


class GroupManagementService:
    """Сервис для управления группами"""

    @staticmethod
    def get_all_groups(active_only: bool = True) -> List[Group]:
        """Возвращает все группы"""
        query = Group.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @staticmethod
    def get_group_by_id(group_id: int) -> Optional[Group]:
        """Возвращает группу по ID"""
        return Group.query.get(group_id)

    @staticmethod
    def create_group(name: str, description: str = None) -> Optional[Group]:
        """Создает новую группу"""
        try:
            if Group.query.filter_by(name=name).first():
                return None
            group = Group(name=name, description=description)
            db.session.add(group)
            db.session.commit()
            return group
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка создания группы: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def update_group(group: Group, name: str = None, description: str = None) -> bool:
        """Обновляет группу"""
        try:
            if name is not None:
                if Group.query.filter(Group.name == name, Group.id != group.id).first():
                    return False
                group.name = name
            if description is not None:
                group.description = description
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка обновления группы: {str(e)}")
            db.session.rollback()
            return False
