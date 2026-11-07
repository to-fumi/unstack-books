from uuid import UUID

from domain.dto import (
    BookListOutput,
    BookListQuery,
    BookOutput,
    CreateBookInput,
    UpdateBookInput,
)
from domain.exceptions import BookAlreadyExistsError, BookNotFoundError
from domain.models import Book
from domain.repositories import BookRepository


class BookService:
    def __init__(self, repository: BookRepository) -> None:
        self._repository = repository

    async def register(self, data: CreateBookInput) -> BookOutput:
        book = Book.register(
            title=data.title,
            author=data.author,
            isbn=data.isbn,
            total_pages=data.total_pages,
            purchased_at=data.purchased_at,
            memo=data.memo,
        )
        await self._ensure_isbn_available(book)
        await self._repository.add(book)
        return BookOutput.from_model(book)

    async def get(self, book_id: UUID) -> BookOutput:
        return BookOutput.from_model(await self._get_or_raise(book_id))

    async def list_books(self, query: BookListQuery) -> BookListOutput:
        books = await self._repository.find_all(
            status=query.status, limit=query.limit, offset=query.offset
        )
        total = await self._repository.count(status=query.status)
        return BookListOutput(items=[BookOutput.from_model(b) for b in books], total=total)

    async def update(self, book_id: UUID, data: UpdateBookInput) -> BookOutput:
        book = await self._get_or_raise(book_id)
        original_isbn = book.isbn
        book.update_info(
            title=data.title,
            author=data.author,
            isbn=data.isbn,
            total_pages=data.total_pages,
            purchased_at=data.purchased_at,
            memo=data.memo,
        )
        # 進捗とステータスが両方来た場合は、明示的なステータスを優先する
        if data.current_page is not None:
            book.record_progress(data.current_page)
        if data.status is not None:
            book.change_status(data.status)
        if book.isbn != original_isbn:
            await self._ensure_isbn_available(book)
        await self._repository.update(book)
        return BookOutput.from_model(book)

    async def delete(self, book_id: UUID) -> None:
        await self._get_or_raise(book_id)
        await self._repository.delete(book_id)

    async def _ensure_isbn_available(self, book: Book) -> None:
        # 同時リクエストのすり抜けは DB のユニーク制約で防ぐ
        if book.isbn is None:
            return
        existing = await self._repository.find_by_isbn(book.isbn)
        if existing is not None and existing.id != book.id:
            raise BookAlreadyExistsError(book.isbn, existing_book_id=existing.id)

    async def _get_or_raise(self, book_id: UUID) -> Book:
        book = await self._repository.get(book_id)
        if book is None:
            raise BookNotFoundError(book_id)
        return book
