from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import Author, Book, Borrowing
from .serializers import AuthorSerializer, BookSerializer, BorrowingSerializer, ReaderRegisterSerializer
from .filters import (
    BookFilter,
    BorrowingFilter,
    AvailableBooksFilterBackend,
    ActiveBorrowingsFilterBackend,
    MinPagesFilterBackend
)
from .throttles import RegisterRateThrottle, BorrowingRateThrottle

Reader = get_user_model()


def landing_page(request):
    return render(request, 'index.html')


class ReaderRegisterAPIView(generics.CreateAPIView):
    queryset = Reader.objects.all()
    serializer_class = ReaderRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'user': serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED, headers=headers)

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
    permission_classes = [IsAuthenticated]
    throttle_classes = [BorrowingRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowingFilter


class AvailableBooksAPIView(generics.ListAPIView):
    queryset = Book.objects.select_related('author').order_by('pk')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, AvailableBooksFilterBackend]
    filterset_class = BookFilter


class ActiveBorrowingsAPIView(generics.ListAPIView):
    queryset = Borrowing.objects.prefetch_related('book', 'reader').order_by('-borrowed_date')
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, ActiveBorrowingsFilterBackend]
    filterset_class = BorrowingFilter