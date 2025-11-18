"""Тесты для main views - минимальный набор."""


class TestMainViews:
    """Тесты для основных представлений."""

    def test_index_unauthenticated(self, client):
        """Тест главной страницы без авторизации."""
        response = client.get("/")
        assert response.status_code == 200
