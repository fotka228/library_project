from datetime import date
from rest_framework import serializers
from .models import Author, Book, Borrowing, Reader


class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'birth_date', 'photo', 'book_count']


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'isbn',
            'published_date', 'pages', 'cover', 'available_copies', 'is_available'
        ]

    def validate_pages(self, value):
        if value <= 0:
            raise serializers.ValidationError("Кількість сторінок має бути більшою за 0.")
        return value

    def validate_isbn(self, value):
        if len(value) != 13:
            raise serializers.ValidationError("ISBN має складатися exactamente з 13 символів.")
        return value


class BookDetailSerializer(BookSerializer):
    author = AuthorSerializer(read_only=True)
    total_borrowings = serializers.SerializerMethodField()

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['total_borrowings']

    def get_total_borrowings(self, obj):
        return obj.borrowings.count()


class BorrowingSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    reader_name = serializers.CharField(source='reader.username', read_only=True)
    days_borrowed = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            'id', 'book', 'reader', 'book_title', 'reader_name',
            'borrowed_date', 'return_date', 'is_returned', 'days_borrowed'
        ]

    def get_days_borrowed(self, obj):
        if obj.is_returned and obj.return_date:
            delta = obj.return_date - obj.borrowed_date
        else:
            delta = date.today() - obj.borrowed_date
        return delta.days