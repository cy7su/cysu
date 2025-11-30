"""Тесты для auth views с максимальным покрытием."""


class TestAuthViews:
    """Тесты для представлений аутентификации."""

    def test_register_page_get(self, client):
        """Тест страницы регистрации GET."""
        response = client.get("/register")
        assert response.status_code == 200
        assert b"register" in response.data

    def test_login_page_get(self, client):
        """Тест страницы входа GET."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"login" in response.data

    def test_logout(self, client):
        """Тест выхода из системы."""
        response = client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
