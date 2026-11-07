from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import BookAlreadyExistsError
from domain.models import Book
from domain.value_objects import Isbn, ReadingStatus
from external.db.entities import BookEntity

ISBN_UNIQUE_INDEX = "ix_books_isbn"


class SqlAlchemyBookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, book: Book) -> None:
        self._session.add(self._to_entity(book))
        await self._commit(book)

    async def get(self, book_id: UUID) -> Book | None:
        entity = await self._session.get(BookEntity, book_id)
        return self._to_model(entity) if entity else None

    async def find_by_isbn(self, isbn: Isbn) -> Book | None:
        entity = await self._session.scalar(select(BookEntity).where(BookEntity.isbn == str(isbn)))
        return self._to_model(entity) if entity else None

    async def find_all(
        self,
        *,
        status: ReadingStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]:
        stmt = select(BookEntity).order_by(BookEntity.created_at.desc(), BookEntity.id.desc())
        if status is not None:
            stmt = stmt.where(BookEntity.status == status)
        result = await self._session.scalars(stmt.limit(limit).offset(offset))
        return [self._to_model(e) for e in result]

    async def count(self, *, status: ReadingStatus | None = None) -> int:
        stmt = select(func.count()).select_from(BookEntity)
        if status is not None:
            stmt = stmt.where(BookEntity.status == status)
        return (await self._session.scalar(stmt)) or 0

    async def update(self, book: Book) -> None:
        await self._session.merge(self._to_entity(book))
        await self._commit(book)

    async def delete(self, book_id: UUID) -> None:
        await self._session.execute(delete(BookEntity).where(BookEntity.id == book_id))
        await self._session.commit()

    async def _commit(self, book: Book) -> None:
        try:
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            constraint = getattr(getattr(e.orig, "__cause__", None), "constraint_name", None)
            if constraint != ISBN_UNIQUE_INDEX or book.isbn is None:
                raise
            existing = await self.find_by_isbn(book.isbn)
            raise BookAlreadyExistsError(
                book.isbn, existing_book_id=existing.id if existing else None
            ) from e

    @staticmethod
    def _to_entity(book: Book) -> BookEntity:
        return BookEntity(
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

    @staticmethod
    def _to_model(entity: BookEntity) -> Book:
        return Book(
            id=entity.id,
            title=entity.title,
            author=entity.author,
            isbn=Isbn(entity.isbn) if entity.isbn else None,
            total_pages=entity.total_pages,
            current_page=entity.current_page,
            status=entity.status,
            purchased_at=entity.purchased_at,
            memo=entity.memo,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
