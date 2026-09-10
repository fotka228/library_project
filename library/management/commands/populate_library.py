from django.core.management.base import BaseCommand
from datetime import date, timedelta
from library.models import Reader, Author, Book, Borrowing


class Command(BaseCommand):
    help = 'Заповнює базу даних тестовими даними'

    def handle(self, *args, **options):
        self.stdout.write('Заповнення бази даних...')

        # Створення читачів
        reader1, _ = Reader.objects.get_or_create(username='john_doe', email='john@example.com', first_name='John', last_name='Doe')
        reader2, _ = Reader.objects.get_or_create(username='jane_smith', email='jane@example.com', first_name='Jane', last_name='Smith')

        # Створення 5 авторів
        authors_data = [
            {"name": "Тарас Шевченко", "bio": "Український поетичний ґеній.", "birth_date": "1814-03-09"},
            {"name": "Леся Українка", "bio": "Видатна українська письменниця.", "birth_date": "1871-02-25"},
            {"name": "Іван Франко", "bio": "Видатний український письменник та поет.", "birth_date": "1856-08-27"},
            {"name": "Джордж Орвелл", "bio": "Англійський письменник і публіцист.", "birth_date": "1903-06-25"},
            {"name": "Артур Конан Дойл", "bio": "Шотландський письменник, автор Шерлока Холмса.", "birth_date": "1859-05-22"},
        ]

        authors = []
        for a in authors_data:
            author, _ = Author.objects.get_or_create(
                name=a["name"],
                defaults={"bio": a["bio"], "birth_date": a["birth_date"]}
            )
            authors.append(author)

        # Створення 10 книг
        books_data = [
            {"title": "Кобзар", "author": authors[0], "isbn": "9789660000001", "pages": 350, "copies": 3},
            {"title": "Гайдамаки", "author": authors[0], "isbn": "9789660000002", "pages": 180, "copies": 2},
            {"title": "Лісова пісня", "author": authors[1], "isbn": "9789660000003", "pages": 120, "copies": 5},
            {"title": "Бояриня", "author": authors[1], "isbn": "9789660000004", "pages": 90, "copies": 0},  # Недоступа
            {"title": "Захар Беркут", "author": authors[2], "isbn": "9789660000005", "pages": 240, "copies": 4},
            {"title": "Укр. украдена щастя", "author": authors[2], "isbn": "9789660000006", "pages": 160, "copies": 1},
            {"title": "1984", "author": authors[3], "isbn": "9789660000007", "pages": 320, "copies": 6},
            {"title": "Колгосп тварин", "author": authors[3], "isbn": "9789660000008", "pages": 140, "copies": 2},
            {"title": "Етюд у багряних тонах", "author": authors[4], "isbn": "9789660000009", "pages": 200, "copies": 3},
            {"title": "Собака Баскервілів", "author": authors[4], "isbn": "9789660000010", "pages": 220, "copies": 0}, # Недоступна
        ]

        books = []
        for b in books_data:
            book, _ = Book.objects.get_or_create(
                isbn=b["isbn"],
                defaults={
                    "title": b["title"],
                    "author": b["author"],
                    "description": f"Опис книги {b['title']}",
                    "published_date": "2020-01-01",
                    "pages": b["pages"],
                    "available_copies": b["copies"]
                }
            )
            books.append(book)

        # Створення 5 позик
        borrowings_data = [
            {"book": books[0], "reader": reader1, "is_returned": True, "return_days_ago": 2},
            {"book": books[2], "reader": reader2, "is_returned": False, "return_days_ago": None},
            {"book": books[4], "reader": reader1, "is_returned": False, "return_days_ago": None},
            {"book": books[6], "reader": reader2, "is_returned": True, "return_days_ago": 5},
            {"book": books[8], "reader": reader1, "is_returned": False, "return_days_ago": None},
        ]

        for bd in borrowings_data:
            borrowing, created = Borrowing.objects.get_or_create(
                book=bd["book"],
                reader=bd["reader"],
                is_returned=bd["is_returned"]
            )
            if created and bd["is_returned"]:
                borrowing.return_date = date.today() - timedelta(days=bd["return_days_ago"])
                borrowing.save()

        self.stdout.write(self.style.SUCCESS('Базу даних успішно заповнено!'))