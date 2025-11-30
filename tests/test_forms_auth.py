"""Дополнительные тесты для форм, аутентификации и оплаты."""

import pytest
from app.models import User, Subject
import uuid


try:
    from app.forms import LoginForm, RegistrationForm as RegisterForm, MaterialForm

    FORMS_AVAILABLE = True
except ImportError:
    FORMS_AVAILABLE = False

try:
    from app.utils.username_validator import (
        contains_forbidden_word,
        has_allowed_characters,
    )

    USERNAME_VALIDATOR_AVAILABLE = True
except ImportError:
    USERNAME_VALIDATOR_AVAILABLE = False


try:
    from app.services.user_management_service import UserManagementService

    USER_MANAGEMENT_AVAILABLE = True
except ImportError:
    USER_MANAGEMENT_AVAILABLE = False


@pytest.mark.skipif(not FORMS_AVAILABLE, reason="Формы недоступны")
class TestForms:
    """Тесты для форм."""

    def test_login_form_valid(self, app):
        """Тест валидной формы входа."""
        with app.app_context():
            form = LoginForm()
            form.username.data = "testuser"
            form.password.data = "testpass"

            assert form.validate()

    def test_login_form_invalid(self, app):
        """Тест невалидной формы входа."""
        with app.app_context():
            form = LoginForm()
            form.username.data = ""
            form.password.data = "testpass"

            assert not form.validate()
            assert "username" in form.errors

    def test_register_form_valid(self, app):
        """Тест валидной формы регистрации."""
        with app.app_context():
            from app.models import Group

            if not Group.query.first():
                test_group = Group(name="Test Group", is_active=True)
                from app.models import db

                db.session.add(test_group)
                db.session.commit()

            form = RegisterForm()
            form.username.data = f"tstusr{uuid.uuid4().hex[:4]}"

            form.email.data = f"tstusr{uuid.uuid4().hex[:4]}@gmail.com"
            form.password.data = "testpass123"
            form.confirm_password.data = "testpass123"
            form.group_id.data = "1"

            assert form.validate()

    def test_register_form_invalid_email(self, app):
        """Тест формы регистрации с невалидным email."""
        with app.app_context():
            form = RegisterForm()
            form.username.data = "testuser"
            form.email.data = "invalid-email"
            form.password.data = "testpass123"
            form.confirm_password.data = "testpass123"

            assert not form.validate()
            assert "email" in form.errors

    def test_material_form_valid(self, app):
        """Тест валидной формы материала."""
        with app.app_context():

            subject = Subject(title="Test Subject")
            from app.models import db

            db.session.add(subject)
            db.session.commit()

            form = MaterialForm()
            form.title.data = "Test Material"
            form.description.data = "Test Description"
            form.type.data = "lecture"
            form.subject_id.choices = [(subject.id, subject.title)]
            form.subject_id.data = subject.id

            assert form.validate()


class TestUsernameValidator:
    """Тесты для username валидации."""

    def test_valid_usernames(self, app):
        """Тест валидных имен пользователей."""
        assert has_allowed_characters("testuser")
        assert has_allowed_characters("user123")
        assert has_allowed_characters("user_name")

    def test_invalid_usernames(self, app):
        """Тест невалидных имен пользователей."""
        assert not has_allowed_characters("")

        assert not has_allowed_characters("a")

        assert not has_allowed_characters("a" * 151)

        assert not has_allowed_characters("user name")

        assert not has_allowed_characters("user@name")

    def test_reserved_usernames(self, app):
        """Тест зарезервированных имен пользователей."""
        reserved_words = ["admin", "root", "administrator", "moderator", "system"]
        for word in reserved_words:
            assert contains_forbidden_word(word), f"'{word}' should be forbidden"


class TestUserManagement:
    """Тесты для управления пользователями."""

    def test_get_accessible_subjects_admin(self, app, db):
        """Тест получения доступных предметов для админа."""
        from app.services.user_management_service import UserManagementService

        with app.app_context():

            admin = User(
                username=f"admin{uuid.uuid4()}",
                email=f"admin{uuid.uuid4()}@gmail.com",
                password="pass",
                is_admin=True,
                admin_mode_enabled=True,
            )
            db.session.add(admin)

            subjects = []
            for i in range(3):
                subject = Subject(title=f"Subject {i}_{uuid.uuid4()}")
                subjects.append(subject)
                db.session.add(subject)

            db.session.commit()

            accessible = UserManagementService.get_accessible_subjects(admin)
            assert len(accessible) == 3

    def test_get_accessible_subjects_regular_user(self, app, db):
        """Тест получения доступных предметов для обычного пользователя."""
        from app.services.user_management_service import UserManagementService

        with app.app_context():

            user = User(
                username=f"user{uuid.uuid4()}",
                email=f"user{uuid.uuid4()}@gmail.com",
                password="pass",
                is_admin=False,
                is_moderator=False,
            )
            db.session.add(user)
            db.session.commit()

            accessible = UserManagementService.get_accessible_subjects(user)
            assert len(accessible) == 0

    def test_can_add_materials_to_subject(self, app, db):
        """Тест проверки возможности добавления материалов к предмету."""
        from app.services.user_management_service import UserManagementService

        with app.app_context():

            admin = User(
                username=f"admin{uuid.uuid4()}",
                email=f"admin{uuid.uuid4()}@gmail.com",
                password="pass",
                is_admin=True,
                admin_mode_enabled=True,
            )
            db.session.add(admin)

            mod = User(
                username=f"mod{uuid.uuid4()}",
                email=f"mod{uuid.uuid4()}@gmail.com",
                password="pass",
                is_admin=False,
                is_moderator=True,
            )
            db.session.add(mod)

            user = User(
                username=f"user{uuid.uuid4()}",
                email=f"user{uuid.uuid4()}@gmail.com",
                password="pass",
            )
            db.session.add(user)

            subject = Subject(title=f"Subject{uuid.uuid4()}")
            db.session.add(subject)
            db.session.commit()

            assert UserManagementService.can_add_materials_to_subject(admin, subject)
            assert not UserManagementService.can_add_materials_to_subject(mod, subject)

            assert not UserManagementService.can_add_materials_to_subject(user, subject)
