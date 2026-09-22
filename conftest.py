import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker

Reader = get_user_model()


@pytest.fixture
def api_client():
    """Анонімний API-клієнт DRF."""
    return APIClient()


@pytest.fixture
def sample_reader(db):
    """Звичайний читач бібліотеки."""
    return Reader.objects.create_user(
        username="reader_taras",
        email="taras@example.com",
        password="ReaderPassword123!",
        phone="+380501112233"
    )


@pytest.fixture
def admin_user(db):
    """Адміністратор бібліотеки (бібліотекар)."""
    return Reader.objects.create_superuser(
        username="librarian_admin",
        email="admin@library.com",
        password="AdminPassword123!"
    )


@pytest.fixture
def auth_client(api_client, sample_reader):
    """Клієнт, авторизований під звичайним читачем."""
    api_client.force_authenticate(user=sample_reader)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Клієнт, авторизований під адміністратором."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def sample_author(db):
    """Тестовий автор книги."""
    return baker.make('library.Author', name="Тарас Шевченко")


@pytest.fixture
def sample_book(db, sample_author):
    """Книга, доступна для видачі."""
    return baker.make(
        'library.Book',
        title="Кобзар",
        author=sample_author,
        pages=280,
        available_copies=3
    )


@pytest.fixture
def out_of_stock_book(db, sample_author):
    """Книга, якої немає в наявності."""
    return baker.make(
        'library.Book',
        title="Рідкісний манускрипт",
        author=sample_author,
        pages=500,
        available_copies=0
    )