class DomainError(Exception):
    pass


class DomainValidationError(DomainError):
    pass


class BookNotFoundError(DomainError):
    def __init__(self, book_id: object) -> None:
        super().__init__(f"Book not found: {book_id}")
        self.book_id = book_id


class BookAlreadyExistsError(DomainError):
    def __init__(self, isbn: object, existing_book_id: object | None = None) -> None:
        super().__init__(f"Book with ISBN {isbn} already exists")
        self.isbn = isbn
        self.existing_book_id = existing_book_id
