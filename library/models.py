from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser


class Reader(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    address = models.TextField(blank=True, null=True, verbose_name="Адреса")
    registration_date = models.DateField(auto_now_add=True, verbose_name="Дата реєстрації")

    class Meta:
        verbose_name = "Читач"
        verbose_name_plural = "Читачі"

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or 'без ім\'я'})"


class Author(models.Model):
    name = models.CharField(max_length=200, verbose_name="Ім'я автора")
    bio = models.TextField(verbose_name="Біографія")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата народження")
    photo = models.ImageField(upload_to='authors/', blank=True, null=True, verbose_name="Фото")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Автори"

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.books.count()


class Book(models.Model):
    title = models.CharField(max_length=300, verbose_name="Назва книги")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name="Автор")
    description = models.TextField(verbose_name="Опис")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    published_date = models.DateField(verbose_name="Дата публікації")
    pages = models.PositiveIntegerField(verbose_name="Кількість сторінок")
    cover = models.ImageField(upload_to='books/', blank=True, null=True, verbose_name="Обкладинка")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Доступні примірники")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.available_copies > 0


class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings', verbose_name="Книга")
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='borrowings', verbose_name="Читач")
    borrowed_date = models.DateField(auto_now_add=True, verbose_name="Дата позики")
    return_date = models.DateField(blank=True, null=True, verbose_name="Дата повернення")
    is_returned = models.BooleanField(default=False, verbose_name="Повернено")

    class Meta:
        verbose_name = "Позика"
        verbose_name_plural = "Позики"

    def __str__(self):
        return f"{self.reader.username} - {self.book.title}"

    @property
    def days_borrowed(self):
        if self.is_returned and self.return_date:
            delta = self.return_date - self.borrowed_date
        else:
            delta = date.today() - self.borrowed_date
        return delta.days