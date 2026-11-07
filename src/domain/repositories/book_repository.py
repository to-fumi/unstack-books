"""Book リポジトリのインターフェース（Protocol）。

service 層はこの Protocol にのみ依存し、実装（external 層）を知らない。
= 依存性逆転の原則 (DIP)
"""

from typing import Protocol
from uuid import UUID

from domain.models import Book
from domain.value_objects import ReadingStatus


class BookRepository(Protocol):
    async def add(self, book: Book) -> None: ...

    async def get(self, book_id: UUID) -> Book | None: ...

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
