"""/books エンドポイント。HTTP の入出力変換のみを担当し、ロジックは service に委譲する。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.dependencies import BookServiceDep
from controller.requests.book import CreateBookRequest, UpdateBookRequest
from controller.responses.book import BookListResponse, BookResponse
from domain.dto import BookListQuery
from domain.value_objects import ReadingStatus

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(body: CreateBookRequest, service: BookServiceDep) -> BookResponse:
    return BookResponse.from_dto(await service.register(body.to_dto()))


@router.get("")
async def list_books(
    service: BookServiceDep,
    status: ReadingStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> BookListResponse:
    result = await service.list_books(BookListQuery(status=status, limit=limit, offset=offset))
    return BookListResponse.from_dto(result, limit=limit, offset=offset)


@router.get("/{book_id}")
async def get_book(book_id: UUID, service: BookServiceDep) -> BookResponse:
    return BookResponse.from_dto(await service.get(book_id))


@router.patch("/{book_id}")
async def update_book(
    book_id: UUID, body: UpdateBookRequest, service: BookServiceDep
) -> BookResponse:
    return BookResponse.from_dto(await service.update(book_id, body.to_dto()))


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, service: BookServiceDep) -> None:
    await service.delete(book_id)
