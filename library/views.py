from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from .models import Author, Book, Borrowing
from .serializers import AuthorSerializer, BookSerializer, BorrowingSerializer
from .filters import (
    BookFilter,
    BorrowingFilter,
    AvailableBooksFilterBackend,
    ActiveBorrowingsFilterBackend,
    MinPagesFilterBackend
)


class AuthorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_url_kwarg = 'author_id'


class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, MinPagesFilterBackend]
    filterset_class = BookFilter


class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BorrowingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.prefetch_related('book', 'reader').all()
    serializer_class = BorrowingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowingFilter


class AvailableBooksAPIView(generics.ListAPIView):
    """Список доступних книг (available_copies > 0)."""
    queryset = Book.objects.select_related('author').order_by('pk')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, AvailableBooksFilterBackend]
    filterset_class = BookFilter


class ActiveBorrowingsAPIView(generics.ListAPIView):
    queryset = Borrowing.objects.prefetch_related('book', 'reader').order_by('-borrowed_date')
    serializer_class = BorrowingSerializer
    filter_backends = [DjangoFilterBackend, ActiveBorrowingsFilterBackend]
    filterset_class = BorrowingFilter