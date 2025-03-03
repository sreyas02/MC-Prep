# Database Design:
# Table: books
# Columns: id (int, primary key), isbn (varchar), 
# title (varchar), author (varchar), year (int)

# Table: members
# Columns: id (int, primary key), member_id (varchar), 
# name (varchar), email (varchar)

# Table: borrowings
# Columns: id (int, primary key), member_id 
# (int, foreign key references members(id)), 
# book_id (int, foreign key references books(id))

from typing import List, Dict
from collections import defaultdict
from threading import Lock

class Book:
    def __init__(self, isbn: str, title: str, author: str, publication_year: int):
        self._isbn = isbn
        self._title = title
        self._author = author
        self._publication_year = publication_year
        self._available = True

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def publication_year(self) -> int:
        return self._publication_year

    @property
    def available(self) -> bool:
        return self._available

    @available.setter
    def available(self, available: bool):
        self._available = available


class Member:
    def __init__(self, member_id: str, name: str, contact_info: str):
        self._member_id = member_id
        self._name = name
        self._contact_info = contact_info
        self._borrowed_books = []

    @property
    def member_id(self) -> str:
        return self._member_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def contact_info(self) -> str:
        return self._contact_info

    @property
    def borrowed_books(self) -> List[Book]:
        return self._borrowed_books

    def borrow_book(self, book: Book):
        self._borrowed_books.append(book)

    def return_book(self, book: Book):
        self._borrowed_books.remove(book)


class LibraryManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.catalog = {}
                    cls._instance.members = {}
                    cls._instance.operation_lock = Lock()
                    cls._instance.MAX_BOOKS_PER_MEMBER = 5
            return cls._instance

    @staticmethod
    def get_instance():
        if LibraryManager._instance is None:
            LibraryManager()
        return LibraryManager._instance

    def add_book(self, book: Book):
        with self.operation_lock:
            self.catalog[book.isbn] = book

    def remove_book(self, isbn: str):
        self.catalog.pop(isbn, None)

    def get_book(self, isbn: str) -> Book:
        return self.catalog.get(isbn)

    def register_member(self, member: Member):
        with self.operation_lock:
            self.members[member.member_id] = member

    def unregister_member(self, member_id: str):
        self.members.pop(member_id, None)

    def get_member(self, member_id: str) -> Member:
        return self.members.get(member_id)

    def borrow_book(self, member_id: str, isbn: str):
        with self.operation_lock:
            member = self.members.get(member_id)
            book = self.catalog.get(isbn)
            if member and book and book.available:
                if len(member.borrowed_books) < self.MAX_BOOKS_PER_MEMBER:
                    member.borrowed_books.append(book)
                    book.available = False
                    print(f"Book borrowed: {book.title} by {member.name}")

    def return_book(self, member_id: str, isbn: str):
        with self.operation_lock:
            member = self.members.get(member_id)
            book = self.catalog.get(isbn)
            if member and book:
                member.borrowed_books.remove(book)
                book.available = True
                print(f"Book returned: {book.title} by {member.name}")

    def search_books(self, keyword: str) -> List[Book]:
        matching_books = [book for book in self.catalog.values() if keyword in book.title or keyword in book.author]
        return matching_books


class LibraryManagementSystemDemo:
    @staticmethod
    def run():
        library_manager = LibraryManager.get_instance()

        # Add books to the catalog
        library_manager.add_book(Book("ISBN1", "Book 1", "Author 1", 2020))
        library_manager.add_book(Book("ISBN2", "Book 2", "Author 2", 2019))
        library_manager.add_book(Book("ISBN3", "Book 3", "Author 3", 2021))

        # Register members
        library_manager.register_member(Member("M1", "John Doe", "john@example.com"))
        library_manager.register_member(Member("M2", "Jane Smith", "jane@example.com"))

        # Borrow books
        library_manager.borrow_book("M1", "ISBN1")
        library_manager.borrow_book("M2", "ISBN2")

        # Return books
        library_manager.return_book("M1", "ISBN1")

        # Search books
        search_results = library_manager.search_books("Book")
        print("Search Results:")
        for book in search_results:
            print(f"{book.title} by {book.author}")

if __name__ == "__main__":
    LibraryManagementSystemDemo.run()