import pytest
from model_bakery import baker


@pytest.mark.django_db
@pytest.mark.models
class TestAuthorModel:
    """Тести для моделі Author."""

    def test_author_str(self, sample_author):
        """__str__ повертає ім'я автора."""
        assert str(sample_author) == "Тарас Шевченко"

    def test_author_book_count_property(self, sample_author):
        """Property book_count повертає точну кількість книг цього автора."""
        assert sample_author.book_count == 0
        baker.make('library.Book', author=sample_author, _quantity=4)
        assert sample_author.book_count == 4


@pytest.mark.django_db
@pytest.mark.models
class TestBookModel:
    """Тести для моделі Book."""

    def test_book_str(self, sample_book):
        """__str__ повертає назву книги."""
        assert str(sample_book) == "Кобзар"

    def test_is_available_true_when_copies_positive(self, sample_book):
        """is_available повертає True, якщо available_copies > 0."""
        assert sample_book.is_available is True

    def test_is_available_false_when_copies_zero(self, out_of_stock_book):
        """is_available повертає False, якщо available_copies == 0."""
        assert out_of_stock_book.is_available is False


@pytest.mark.django_db
@pytest.mark.models
class TestBorrowingModel:
    """Тести для моделі Borrowing (Позика книги)."""

    def test_borrowing_default_not_returned(self, sample_book, sample_reader):
        """Нова позика за замовчуванням має статус is_returned=False."""
        borrowing = baker.make(
            'library.Borrowing',
            book=sample_book,
            reader=sample_reader
        )
        assert borrowing.is_returned is False