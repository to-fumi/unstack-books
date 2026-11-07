"""依存性の組み立て（Composition Root）。

ここでのみ「domain の Protocol」と「external の実装」を結びつける。
controller はここで定義された依存関数を Depends() で受け取る。
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories import BookRepository
from external.db.client import get_session
from external.db.repositories import SqlAlchemyBookRepository
from services.book_service import BookService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_book_repository(session: SessionDep) -> BookRepository:
    return SqlAlchemyBookRepository(session)


def get_book_service(
    repository: Annotated[BookRepository, Depends(get_book_repository)],
) -> BookService:
    return BookService(repository)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]
