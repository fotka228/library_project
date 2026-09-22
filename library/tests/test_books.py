import pytest
from django.urls import reverse
from library.models import Book


@pytest.mark.django_db
@pytest.mark.books
class TestBookAPI:

    url_books = reverse('library:book_list_create')

    def test_get_books_anonymous_allowed(self, api_client, sample_book):
        response = api_client.get(self.url_books)
        assert response.status_code == 200
        data = response.data.get('results') if isinstance(response.data, dict) else response.data
        assert len(data) >= 1

    def test_create_book_anonymous_forbidden(self, api_client, sample_author):
        payload = {
            "title": "Холодний яр",
            "author_id": sample_author.id,
            "pages": 450,
            "available_copies": 5,
            "published_date": "1932-01-01"
        }
        response = api_client.post(self.url_books, payload)
        assert response.status_code == 401

    def test_create_book_regular_reader_forbidden(self, auth_client, sample_author):
        payload = {
            "title": "Книга від читача",
            "author_id": sample_author.id,
            "pages": 200,
            "available_copies": 1,
            "published_date": "2020-01-01"
        }
        response = auth_client.post(self.url_books, payload)
        assert response.status_code == 403

    def test_create_book_admin_success(self, admin_client, sample_author):
        payload = {
            "title": "Захар Беркут",
            "author_id": sample_author.id,
            "pages": 220,
            "available_copies": 2,
            "published_date": "1883-01-01"
        }
        response = admin_client.post(self.url_books, payload)
        assert response.status_code == 201
        assert Book.objects.filter(title=payload['title']).exists()

    @pytest.mark.parametrize("invalid_pages, invalid_copies", [
        (0, 5),
        (-10, 2),
    ])
    def test_create_book_invalid_data(self, admin_client, sample_author, invalid_pages, invalid_copies):
        payload = {
            "title": "Помилкова книга",
            "author_id": sample_author.id,
            "pages": invalid_pages,
            "available_copies": invalid_copies,
            "published_date": "2021-01-01"
        }
        response = admin_client.post(self.url_books, payload)
        assert response.status_code == 400

    def test_filter_available_books(self, api_client, sample_book, out_of_stock_book):
        try:
            url_available = reverse('library:available_books')
        except Exception:
            url_available = '/api/books/available/'

        response = api_client.get(url_available)
        assert response.status_code == 200
        data = response.data.get('results') if isinstance(response.data, dict) else response.data
        titles = [item['title'] for item in data]
        assert sample_book.title in titles
        assert out_of_stock_book.title not in titles