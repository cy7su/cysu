from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .. import db
from ..models import Group, Subject, SubjectGroup, User


class UserManagementService:

    @staticmethod
    def is_effective_admin(user: User) -> bool:
        return user.is_admin and user.admin_mode_enabled

    @staticmethod
    def can_manage_materials(user: User) -> bool:
        return (user.is_admin and user.admin_mode_enabled) or user.is_moderator

    @staticmethod
    def can_see_all_subjects(user: User) -> bool:
        return user.is_admin and user.admin_mode_enabled

    @staticmethod
    def get_accessible_subjects(user: User) -> List[Subject]:
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
        if user.is_admin and user.admin_mode_enabled:
            return True
        elif user.is_moderator and user.moderator_mode_enabled and user.group_id:
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
        return UserManagementService.can_add_materials_to_subject(user, subject)

    @staticmethod
    def has_active_subscription(user: User) -> bool:

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
        if not user.is_admin:
            return False
        user.admin_mode_enabled = not user.admin_mode_enabled
        db.session.commit()
        return user.admin_mode_enabled

    @staticmethod
    def toggle_moderator_mode(user: User) -> bool:
        if not user.is_moderator:
            return False
        user.moderator_mode_enabled = not user.moderator_mode_enabled
        db.session.commit()
        return user.moderator_mode_enabled

    @staticmethod
    def grant_manual_subscription(user: User, days: int = 30) -> bool:
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
    def change_user_email(
        user: User, new_email: str, is_admin_change: bool = True
    ) -> bool:
        try:
            existing_user = User.query.filter(
                User.email == new_email, User.id != user.id
            ).first()
            if existing_user:
                return False

            user.email = new_email
            user.is_verified = False
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка изменения email: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def change_user_telegram_id(user: User, new_telegram_id: int) -> bool:
        try:
            from app.models import TelegramUser

            existing_tg_user = TelegramUser.query.filter(
                TelegramUser.telegram_id == new_telegram_id,
                TelegramUser.user_id != user.id,
            ).first()
            if existing_tg_user:
                return False

            tg_user = TelegramUser.query.filter_by(telegram_id=new_telegram_id).first()
            if tg_user:
                tg_user.user_id = user.id
            else:
                tg_user = TelegramUser(telegram_id=new_telegram_id, user_id=user.id)
                db.session.add(tg_user)
            old_tg_user = TelegramUser.query.filter_by(user_id=user.id).first()
            if old_tg_user and old_tg_user.telegram_id != new_telegram_id:
                old_tg_user.user_id = None

            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Ошибка изменения telegram_id: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def change_user_id(user: User, new_user_id: int) -> bool:
        try:
            existing_user = User.query.filter(User.id == new_user_id).first()
            if existing_user:
                return False
            old_id = user.id
            from flask import current_app
            from sqlalchemy import text

            engine = db.engine

            with engine.connect() as conn:
                trans = conn.begin()

                try:
                    conn.execute(
                        text("UPDATE user SET id = :new_id WHERE id = :old_id"),
                        {"new_id": new_user_id, "old_id": old_id},
                    )
                    conn.execute(
                        text(
                            "UPDATE submission SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE payment SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE ticket SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE ticket SET admin_id = :new_id WHERE admin_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE ticket_message SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE chat_message SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE material SET created_by = :new_id WHERE created_by = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE subject SET created_by = :new_id WHERE created_by = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE telegram_user SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE email_verification SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE notification SET user_id = :new_id WHERE user_id = :old_id"
                        ),
                        {"new_id": new_user_id, "old_id": old_id},
                    )

                    conn.execute(
                        text(
                            "UPDATE submission SET file = REPLACE(file, :old_path, :new_path) WHERE user_id = :new_id"
                        ),
                        {
                            "old_path": f"/{old_id}/",
                            "new_path": f"/{new_user_id}/",
                            "new_id": new_user_id,
                        },
                    )

                    trans.commit()

                    current_app.logger.info(
                        f"User ID изменен: {old_id} -> {new_user_id}"
                    )
                    return True

                except Exception as e:
                    trans.rollback()
                    current_app.logger.error(f"Ошибка при изменении user ID: {str(e)}")
                    raise

        except Exception as e:
            from flask import current_app

            current_app.logger.error(
                f"Ошибка изменения user ID без ограничений: {str(e)}"
            )
            return False

    @staticmethod
    def set_user_role(user: User, role: str) -> bool:
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
        return User.query.count()

    @staticmethod
    def get_users_count_by_role() -> Dict[str, int]:
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

    @staticmethod
    def get_all_groups(active_only: bool = True) -> List[Group]:
        query = Group.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @staticmethod
    def get_group_by_id(group_id: int) -> Optional[Group]:
        return Group.query.get(group_id)

    @staticmethod
    def create_group(name: str, description: str = None) -> Optional[Group]:
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
