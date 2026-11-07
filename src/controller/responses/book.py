from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.dto import BookListOutput, BookOutput
from domain.value_objects import ReadingStatus


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    def from_dto(cls, dto: BookOutput) -> BookResponse:
        return cls.model_validate(dto)


class BookListResponse(BaseModel):
    items: list[BookResponse]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_dto(cls, dto: BookListOutput, *, limit: int, offset: int) -> BookListResponse:
        return cls(
            items=[BookResponse.from_dto(b) for b in dto.items],
            total=dto.total,
            limit=limit,
            offset=offset,
        )
