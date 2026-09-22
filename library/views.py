from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import Author, Book, Borrowing
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    BorrowingSerializer,
    ReaderRegisterSerializer
)
from .filters import (
    BookFilter,
    BorrowingFilter,
    AvailableBooksFilterBackend,
    ActiveBorrowingsFilterBackend,
    MinPagesFilterBackend
)
from .throttles import RegisterRateThrottle, BorrowingRateThrottle

Reader = get_user_model()


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


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
    permission_classes = [IsAdminUserOrReadOnly]


class AuthorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_url_kwarg = 'author_id'
    permission_classes = [IsAdminUserOrReadOnly]


class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, MinPagesFilterBackend]
    filterset_class = BookFilter


class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class BorrowingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [BorrowingRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowingFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.select_related('book', 'reader').all()
        if user.is_staff:
            return queryset
        return queryset.filter(reader=user)


class AvailableBooksAPIView(generics.ListAPIView):
    queryset = Book.objects.select_related('author').order_by('pk')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, AvailableBooksFilterBackend]
    filterset_class = BookFilter


class ActiveBorrowingsAPIView(generics.ListAPIView):
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, ActiveBorrowingsFilterBackend]
    filterset_class = BorrowingFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.select_related('book', 'reader').order_by('-borrowed_date')
        if user.is_staff:
            return queryset
        return queryset.filter(reader=user)