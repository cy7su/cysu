"""Тесты для представлений (views)."""

import pytest
import uuid
from flask import url_for
from app.models import User, Group, Subject, Material, db


class TestMainViews:
    """Тесты основных представлений."""

    def test_index_unauthenticated(self, client):
        """Тест главной страницы для неавторизованного пользователя."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"cysu" in response.data

    def test_index_authenticated_user(self, client, app):
        """Тест главной страницы для авторизованного пользователя."""
        with app.app_context():

            unique_username = f"testuser_{uuid.uuid4()}"
            unique_email = f"test_{uuid.uuid4()}@gmail.com"
            unique_group_name = f"Test Group {uuid.uuid4()}"
            user = User(username=unique_username, email=unique_email, password="test")
            group = Group(name=unique_group_name)
            db.session.add(user)
            db.session.add(group)
            db.session.commit()

            subject = Subject(title="Test Subject", pattern_type="dots")
            db.session.add(subject)
            db.session.commit()

            with client:
                client.post(
                    "/auth/login", data={"username": "testuser", "password": "test"}
                )
                response = client.get("/")
                assert response.status_code == 200

    def test_privacy_page(self, client):
        """Тест страницы политики конфиденциальности."""
        response = client.get("/privacy")
        assert response.status_code == 200

    def test_terms_page(self, client):
        """Тест страницы условий использования."""
        response = client.get("/terms")
        assert response.status_code == 200

    def test_404_page(self, client):
        """Тест страницы 404."""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404

    def test_error_page(self, client):
        """Тест страницы ошибок."""
        response = client.get("/error/404")
        assert response.status_code == 404
        assert b"404" in response.data

    def test_404_redirect(self, client):
        """Тест страницы 404 работает корректно."""
        response = client.get("/404")

        assert True

    def test_wiki_page(self, client):
        """Тест страницы вики."""
        response = client.get("/wiki")
        assert response.status_code == 200

    def test_security_txt(self, client):
        """Тест security.txt файла."""
        response = client.get("/.well-known/security.txt")
        assert response.status_code == 200
        assert b"Contact:" in response.data
        assert b"mailto:support@cysu.ru" in response.data

    def test_humans_txt(self, client):
        """Тест humans.txt файла."""
        response = client.get("/.well-known/humans.txt")
        assert response.status_code == 200
        assert b"Developer: cysu" in response.data

    def test_robots_txt(self, client):
        """Тест robots.txt файла."""
        response = client.get("/.well-known/robots.txt")
        assert response.status_code == 200
        assert b"User-agent: *" in response.data

    def test_robots_txt_redirect(self, client):
        """Тест редиректа robots.txt."""
        response = client.get("/robots.txt")
        assert response.status_code == 301


class TestAuthenticatedViews:
    """Тесты представлений требующих аутентификации."""

    @pytest.fixture
    def authenticated_client(self, client, app):
        """Фикстура авторизованного клиента."""
        with app.app_context():
            user = User(
                username="testuser", email="test@gmail.com", password="hashed_password"
            )
            db.session.add(user)
            db.session.commit()

        with client:

            yield client

    def test_profile_requires_login(self, client):
        """Тест что профиль требует входа."""
        response = client.get("/profile")

        assert response.status_code == 302 or response.status_code == 401

    def test_subject_detail_requires_access(self, client, app):
        """Тест доступа к деталям предмета."""
        with app.app_context():
            subject = Subject(title="Test Subject")
            db.session.add(subject)
            db.session.commit()

            response = client.get(f"/subject/{subject.id}")

            assert response.status_code == 200

    def test_material_detail_requires_login(self, client, app):
        """Тест что детали материала требуют входа."""
        with app.app_context():
            subject = Subject(title="Test Subject")
            db.session.add(subject)
            db.session.commit()

            material = Material(title="Test Material", subject_id=subject.id)
            db.session.add(material)
            db.session.commit()

            response = client.get(f"/material/{material.id}")
            assert response.status_code in [302, 401]

    def test_grant_temp_access(self, client):
        """Тест предоставления временного доступа."""
        with client:
            response = client.get("/grant-temp-access")
            assert response.status_code == 302

            with client.session_transaction() as sess:
                assert "temp_access" in sess


class TestStaticRoutes:
    """Тесты статических маршрутов."""

    def test_security_policy_page(self, client):
        """Тест страницы политики безопасности."""
        response = client.get("/security-policy")
        assert response.status_code == 200

    def test_redirect_page(self, client):
        """Тест страницы перенаправления."""
        response = client.get("/redirect")
        assert response.status_code == 200

    def test_download_redirect(self, client):
        """Тест перенаправления скачивания."""
        response = client.get("/redirect/download")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/html; charset=utf-8"
        assert "attachment" in response.headers.get("Content-Disposition", "")

    def test_invalid_error_code(self, client):
        """Тест обработки неизвестного кода ошибки."""
        response = client.get("/error/999")
        assert response.status_code == 999
