"""Тесты для моделей базы данных."""

import pytest
import uuid
from datetime import datetime, timedelta
from app.models import (
    User,
    Group,
    Subject,
    Material,
    Payment,
    Ticket,
    EmailVerification,
    PasswordReset,
    ShortLink,
    Notification,
    SiteSettings,
    TelegramUser,
    db,
)


class TestGroup:
    """Тесты для модели Group."""

    def test_group_creation(self, app):
        """Тест создания группы."""
        with app.app_context():
            unique_name = f"Test Group {uuid.uuid4()}"
            group = Group(name=unique_name, description="Description")
            db.session.add(group)
            db.session.commit()

            assert group.id is not None
            assert group.name == unique_name
            assert group.description == "Description"
            assert group.is_active is True
            assert group.created_at is not None

    def test_group_repr(self, app):
        """Тест строкового представления группы."""
        with app.app_context():
            unique_name = f"Test Group {uuid.uuid4()}"
            group = Group(name=unique_name)
            assert str(group) == f"<Group {unique_name}>"


class TestUser:
    """Тесты для модели User."""

    def test_user_creation(self, app):
        """Тест создания пользователя."""
        with app.app_context():
            unique_username = f"testuser{uuid.uuid4()}"
            unique_email = f"test{uuid.uuid4()}@gmail.com"
            user = User(
                username=unique_username, email=unique_email, password="hashed_password"
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == unique_username
            assert user.email == unique_email
            assert user.is_admin is False
            assert user.is_moderator is False
            assert user.is_verified is False

    def test_user_admin_methods(self, app):
        """Тест методов администрирования пользователя."""
        with app.app_context():

            unique_username = f"regular{uuid.uuid4()}"
            unique_email = f"regular{uuid.uuid4()}@gmail.com"
            user = User(
                username=unique_username,
                email=unique_email,
                password="pass",
                is_admin=False,
                admin_mode_enabled=False,
            )
            assert not user.is_effective_admin()
            assert not user.can_manage_materials()
            assert not user.can_see_all_subjects()

            admin_username = f"admin{uuid.uuid4()}"
            admin_email = f"admin{uuid.uuid4()}@gmail.com"
            admin = User(
                username=admin_username,
                email=admin_email,
                password="pass",
                is_admin=True,
                admin_mode_enabled=True,
            )
            assert admin.is_effective_admin()
            assert admin.can_manage_materials()
            assert admin.can_see_all_subjects()

            mod_username = f"mod{uuid.uuid4()}"
            mod_email = f"mod{uuid.uuid4()}@gmail.com"
            mod = User(
                username=mod_username,
                email=mod_email,
                password="pass",
                is_moderator=True,
            )
            assert mod.can_manage_materials()

    def test_user_role_display(self, app):
        """Тест отображения роли пользователя."""
        with app.app_context():
            user_username = f"user{uuid.uuid4()}"
            user_email = f"user{uuid.uuid4()}@gmail.com"
            user = User(
                username=user_username,
                email=user_email,
                password="pass",
                is_admin=False,
                is_moderator=False,
            )

            admin_e_username = f"admin_e{uuid.uuid4()}"
            admin_e_email = f"admin_e{uuid.uuid4()}@gmail.com"
            admin_enabled = User(
                username=admin_e_username,
                email=admin_e_email,
                password="pass",
                is_admin=True,
                admin_mode_enabled=True,
            )

            admin_d_username = f"admin_d{uuid.uuid4()}"
            admin_d_email = f"admin_d{uuid.uuid4()}@gmail.com"
            admin_disabled = User(
                username=admin_d_username,
                email=admin_d_email,
                password="pass",
                is_admin=True,
                admin_mode_enabled=False,
            )

            mod_username = f"mod{uuid.uuid4()}"
            mod_email = f"mod{uuid.uuid4()}@gmail.com"
            mod = User(
                username=mod_username,
                email=mod_email,
                password="pass",
                is_admin=False,
                is_moderator=True,
            )

            assert user.get_role_display() == "Пользователь"
            assert admin_enabled.get_role_display() == "Администратор (Админ режим)"
            assert (
                admin_disabled.get_role_display()
                == "Администратор (Пользователь режим)"
            )
            assert mod.get_role_display() == "Модератор"


class TestSubject:
    """Тесты для модели Subject."""

    def test_subject_creation(self, app):
        """Тест создания предмета."""
        with app.app_context():
            unique_title = f"Математика {uuid.uuid4()}"
            subject = Subject(
                title=unique_title, description="Высшая математика", pattern_type="dots"
            )
            db.session.add(subject)
            db.session.commit()

            assert subject.id is not None
            assert subject.title == unique_title
            assert subject.description == "Высшая математика"
            assert subject.pattern_type == "dots"


class TestMaterial:
    """Тесты для модели Material."""

    def test_material_creation(self, app):
        """Тест создания материала."""
        with app.app_context():
            subject_title = f"Test Subject {uuid.uuid4()}"
            subject = Subject(title=subject_title)
            db.session.add(subject)
            db.session.commit()

            material_title = f"Тестовый материал {uuid.uuid4()}"
            material = Material(
                title=material_title,
                description="Описание материала",
                type="pdf",
                subject_id=subject.id,
            )
            db.session.add(material)
            db.session.commit()

            assert material.id is not None
            assert material.title == material_title
            assert material.type == "pdf"
            assert material.subject_id == subject.id


class TestPayment:
    """Тесты для модели Payment."""

    def test_payment_creation(self, app):
        """Тест создания платежа."""
        with app.app_context():
            user_username = f"payer{uuid.uuid4()}"
            user_email = f"payer{uuid.uuid4()}@gmail.com"
            user = User(username=user_username, email=user_email, password="pass")
            db.session.add(user)
            db.session.commit()

            unique_payment_id = f"test_payment_{uuid.uuid4()}"
            payment = Payment(
                user_id=user.id,
                yookassa_payment_id=unique_payment_id,
                amount=1000.00,
                currency="RUB",
                status="pending",
            )
            db.session.add(payment)
            db.session.commit()

            assert payment.id is not None
            assert payment.yookassa_payment_id == unique_payment_id
            assert payment.amount == 1000.00
            assert payment.currency == "RUB"
            assert payment.status == "pending"


class TestTicket:
    """Тесты для модели Ticket."""

    def test_ticket_creation(self, app):
        """Тест создания тикета."""
        with app.app_context():
            user_username = f"customer{uuid.uuid4()}"
            user_email = f"customer{uuid.uuid4()}@gmail.com"
            user = User(username=user_username, email=user_email, password="pass")
            db.session.add(user)
            db.session.commit()

            unique_subject = f"Проблема с оплатой {uuid.uuid4()}"
            ticket = Ticket(
                user_id=user.id,
                subject=unique_subject,
                message="Не прошла оплата подписки",
            )
            db.session.add(ticket)
            db.session.commit()

            assert ticket.id is not None
            assert ticket.subject == unique_subject
            assert ticket.message == "Не прошла оплата подписки"
            assert ticket.status == "pending"


class TestEmailVerification:
    """Тесты для модели EmailVerification."""

    def test_code_generation(self, app):
        """Тест генерации кода верификации."""
        with app.app_context():
            code = EmailVerification.generate_code()
            assert len(code) == 6
            assert code.isdigit()

    def test_verification_creation(self, app):
        """Тест создания верификации."""
        with app.app_context():
            unique_email = f"test{uuid.uuid4()}@gmail.com"
            verification = EmailVerification.create_verification(
                user_id=1, email=unique_email, expires_in_minutes=15
            )

            assert verification.user_id == 1
            assert verification.email == unique_email
            assert len(verification.code) == 6
            assert not verification.is_used

            assert verification.expires_at > datetime.utcnow()


class TestShortLink:
    """Тесты для модели ShortLink."""

    def test_code_generation(self, app):
        """Тест генерации короткого кода."""
        with app.app_context():
            code = ShortLink.generate_code()
            assert len(code) == 3
            assert code.isalnum()

    def test_unique_creation(self, app):
        """Тест создания уникальной короткой ссылки."""
        with app.app_context():
            unique_url = f"https://gmail.com/test{uuid.uuid4()}"
            link = ShortLink.create_unique(unique_url)
            assert link is not None
            assert len(link.code) >= 3
            assert link.original_url == unique_url
            assert link.clicks == 0


class TestSiteSettings:
    """Тесты для модели SiteSettings."""

    def test_setting_operations(self, app):
        """Тест операций с настройками."""
        with app.app_context():
            unique_key = f"test_key_{uuid.uuid4()}"

            setting = SiteSettings.set_setting(unique_key, "test_value", "Test setting")
            assert setting.key == unique_key
            assert setting.value == "test_value"

            value = SiteSettings.get_setting(unique_key)
            assert value == "test_value"

            default_value = SiteSettings.get_setting("nonexistent", "default")
            assert default_value == "default"
