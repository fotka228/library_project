import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

Reader = get_user_model()


@pytest.mark.django_db
@pytest.mark.auth
class TestAuthAPI:
    """Тестування автентифікації та реєстрації читача."""

    url_register = reverse('library:reader_register')
    url_token = reverse('token_obtain_pair')
    url_refresh = reverse('token_refresh')

    def test_reader_registration_success(self, api_client):
        """Успішна реєстрація нового читача: пароль захешовано, у відповіді паролю немає."""
        payload = {
            "username": "lesia_ukrainka",
            "email": "lesia@example.com",
            "phone": "+380509998877",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!"
        }
        response = api_client.post(self.url_register, payload)

        assert response.status_code == 201
        assert 'password' not in response.data

        reader = Reader.objects.get(username="lesia_ukrainka")
        assert reader.check_password("SecurePassword123!") is True

    def test_reader_registration_password_mismatch(self, api_client):
        """Спроба реєстрації з різними паролями повертає 400 Bad Request."""
        payload = {
            "username": "mismatch_user",
            "email": "mismatch@example.com",
            "password": "Password123!",
            "password_confirm": "OtherPassword456!"
        }
        response = api_client.post(self.url_register, payload)
        assert response.status_code == 400
        assert "password_confirm" in response.data

    def test_login_obtain_tokens(self, api_client, sample_reader):
        """Отримання пари JWT access/refresh токенів для дійсного читача."""
        payload = {
            "username": "reader_taras",
            "password": "ReaderPassword123!"
        }
        response = api_client.post(self.url_token, payload)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    # --- Бонусне завдання: Тестування Throttling ---
    def test_throttling_on_registration(self, api_client):
        """Швидкі 6 запитів на реєстрацію перевищують ліміт (5/min) і повертають 429."""
        payload = {
            "username": "throttled_user",
            "email": "throttle@example.com",
            "password": "Password123!",
            "password_confirm": "Password123!"
        }
        
        statuses = []
        for i in range(6):
            p = payload.copy()
            p["username"] = f"user_{i}"
            p["email"] = f"user_{i}@example.com"
            res = api_client.post(self.url_register, p)
            statuses.append(res.status_code)

        assert 429 in statuses