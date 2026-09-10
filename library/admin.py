from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Reader, Author, Book, Borrowing


@admin.register(Reader)
class ReaderAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'registration_date', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('phone', 'address')}),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'book_count')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies', 'is_available')
    list_filter = ('author', 'published_date')
    search_fields = ('title', 'isbn', 'author__name')


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('book', 'reader', 'borrowed_date', 'return_date', 'is_returned', 'days_borrowed')
    list_filter = ('is_returned', 'borrowed_date')
    search_fields = ('book__title', 'reader__username')