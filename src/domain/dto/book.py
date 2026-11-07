from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from domain.models import Book
from domain.value_objects import ReadingStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateBookInput:
    title: str
    author: str | None = None
    isbn: str | None = None
    total_pages: int | None = None
    purchased_at: date | None = None
    memo: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateBookInput:
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    total_pages: int | None = None
    current_page: int | None = None
    status: ReadingStatus | None = None
    purchased_at: date | None = None
    memo: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class BookListQuery:
    status: ReadingStatus | None = None
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class BookOutput:
    id: UUID
    title: str
    author: str | None
    isbn: str | None
    total_pages: int | None
    current_page: int
    status: ReadingStatus
    purchased_at: date | None
    memo: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, book: Book) -> BookOutput:
        return cls(
            id=book.id,
            title=book.title,
            author=book.author,
            isbn=str(book.isbn) if book.isbn else None,
            total_pages=book.total_pages,
            current_page=book.current_page,
            status=book.status,
            purchased_at=book.purchased_at,
            memo=book.memo,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class BookListOutput:
    items: list[BookOutput]
    total: int
