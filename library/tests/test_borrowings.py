import pytest
from django.urls import reverse
from model_bakery import baker


@pytest.mark.django_db
@pytest.mark.borrowings
class TestBorrowingAPI:
    """Тестування операцій з позиками книг."""

    url_borrowings = reverse('library:borrowing_list_create')

    def test_get_borrowings_anonymous_unauthorized(self, api_client):
        """Анонімний користувач не може переглядати історію позик (401)."""
        response = api_client.get(self.url_borrowings)
        assert response.status_code == 401

    def test_reader_sees_only_own_borrowings(self, api_client, sample_reader):
        """Читач бачить у списку лише ті позики, які він сам оформив."""
        other_reader = baker.make('library.Reader', username="other_user")
        book = baker.make('library.Book', published_date="2020-01-01")

        baker.make('library.Borrowing', reader=sample_reader, book=book, _quantity=2)
        baker.make('library.Borrowing', reader=other_reader, book=book, _quantity=1)

        api_client.force_authenticate(user=sample_reader)
        response = api_client.get(self.url_borrowings)

        assert response.status_code == 200
        data = response.data.get('results') if isinstance(response.data, dict) else response.data
        assert len(data) == 2
        for item in data:
            reader_val = item['reader']
            # Підтримка випадку, коли reader повертається як ID або як словник/об'єкт
            if isinstance(reader_val, dict):
                assert reader_val['id'] == sample_reader.id
            else:
                assert reader_val == sample_reader.id

    def test_reader_create_borrowing_success(self, auth_client, sample_book, sample_reader):
        """Авторизований читач може успішно взяти доступну книгу (201 Created)."""
        payload = {
            "book": sample_book.id,
            "reader": sample_reader.id
        }
        response = auth_client.post(self.url_borrowings, payload)
        assert response.status_code in [200, 201]