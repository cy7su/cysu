"""Тесты для payment views - минимальный набор."""


class TestPaymentViews:
    """Тесты для представлений платежной системы."""

    def test_payment_page_access_redirect(self, client):
        """Тест доступа к странице платежей без авторизации."""
        response = client.get("/subscription")
        assert response.status_code == 302
