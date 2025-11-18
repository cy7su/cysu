"""Простые тесты для проверки запуска приложения."""

import pytest
import uuid


class TestApp:
    """Базовые тесты приложения."""

    def test_app_creation(self, app):
        """Тест создания Flask приложения."""
        assert app is not None
        assert hasattr(app, "config")

    def test_app_context(self, app):
        """Тест контекста приложения."""
        with app.app_context():
            assert app.config["TESTING"] is True

    def test_database_connection(self, app, db):
        """Тест подключения к базе данных."""
        with app.app_context():
            # Проверяем что можем создать таблицы
            from app.models import User

            db.create_all()
            # Создаем тестового пользователя и проверяем работу
            unique_username = f"test_db_{uuid.uuid4()}"
            unique_email = f"test_db_{uuid.uuid4()}@gmail.com"
            user = User(username=unique_username, email=unique_email, password="test")
            db.session.add(user)
            db.session.commit()
            assert User.query.count() == 1
            assert User.query.first().username == unique_username

    def test_blueprints_registration(self, app):
        """Тест регистрации blueprints."""
        # Проверяем что основные blueprints зарегистрированы
        assert "main" in app.blueprints
        assert "auth" in app.blueprints
        assert "api" in app.blueprints
        assert "payment" in app.blueprints
        assert "tickets" in app.blueprints
        assert "admin" in app.blueprints

    def test_config_values(self, app):
        """Тест значений конфигурации."""
        assert app.config["TESTING"] is True
        assert app.config["SECRET_KEY"] == "test_secret_key"
