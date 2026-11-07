from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID, uuid7

from domain.exceptions import DomainValidationError
from domain.value_objects import Isbn, ReadingStatus


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True, kw_only=True)
class Book:
    title: str
    author: str | None = None
    isbn: Isbn | None = None
    total_pages: int | None = None
    current_page: int = 0
    status: ReadingStatus = ReadingStatus.UNREAD
    purchased_at: date | None = None
    memo: str | None = None
    id: UUID = field(default_factory=uuid7)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def __post_init__(self) -> None:
        self._validate()

    @classmethod
    def register(
        cls,
        *,
        title: str,
        author: str | None = None,
        isbn: str | None = None,
        total_pages: int | None = None,
        purchased_at: date | None = None,
        memo: str | None = None,
    ) -> Book:
        return cls(
            title=title,
            author=author,
            isbn=Isbn(isbn) if isbn else None,
            total_pages=total_pages,
            purchased_at=purchased_at,
            memo=memo,
        )

    def update_info(
        self,
        *,
        title: str | None = None,
        author: str | None = None,
        isbn: str | None = None,
        total_pages: int | None = None,
        purchased_at: date | None = None,
        memo: str | None = None,
    ) -> None:
        if title is not None:
            self.title = title
        if author is not None:
            self.author = author
        if isbn is not None:
            self.isbn = Isbn(isbn)
        if total_pages is not None:
            self.total_pages = total_pages
        if purchased_at is not None:
            self.purchased_at = purchased_at
        if memo is not None:
            self.memo = memo
        self._validate()
        self._touch()

    def change_status(self, status: ReadingStatus) -> None:
        if status == ReadingStatus.COMPLETED and self.total_pages is not None:
            self.current_page = self.total_pages
        if status == ReadingStatus.UNREAD:
            self.current_page = 0
        self.status = status
        self._touch()

    def record_progress(self, current_page: int) -> None:
        self.current_page = current_page
        self._validate()
        if self.total_pages is not None and current_page >= self.total_pages:
            self.status = ReadingStatus.COMPLETED
        elif current_page > 0:
            self.status = ReadingStatus.READING
        else:
            self.status = ReadingStatus.UNREAD
        self._touch()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise DomainValidationError("title must not be empty")
        if self.total_pages is not None and self.total_pages <= 0:
            raise DomainValidationError("total_pages must be positive")
        if self.current_page < 0:
            raise DomainValidationError("current_page must be >= 0")
        if self.total_pages is not None and self.current_page > self.total_pages:
            raise DomainValidationError("current_page must be <= total_pages")

    def _touch(self) -> None:
        self.updated_at = _now()
