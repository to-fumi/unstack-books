from typing import Protocol
from uuid import UUID

from domain.models import Book
from domain.value_objects import Isbn, ReadingStatus


class BookRepository(Protocol):
    """add / update は ISBN が重複した場合 BookAlreadyExistsError を送出する。"""

    async def add(self, book: Book) -> None: ...

    async def get(self, book_id: UUID) -> Book | None: ...

    async def find_by_isbn(self, isbn: Isbn) -> Book | None: ...

    async def find_all(
        self,
        *,
        status: ReadingStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]: ...

    async def count(self, *, status: ReadingStatus | None = None) -> int: ...

    async def update(self, book: Book) -> None: ...

    async def delete(self, book_id: UUID) -> None: ...
