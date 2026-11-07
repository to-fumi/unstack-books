"""Book API のリクエストスキーマ（入力バリデーション）。"""

from datetime import date

from pydantic import BaseModel, Field

from domain.dto import CreateBookInput, UpdateBookInput
from domain.value_objects import ReadingStatus


class CreateBookRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255, examples=["リーダブルコード"])
    author: str | None = Field(default=None, max_length=255, examples=["Dustin Boswell"])
    isbn: str | None = Field(default=None, examples=["978-4873115658"])
    total_pages: int | None = Field(default=None, gt=0, examples=[260])
    purchased_at: date | None = None
    memo: str | None = None

    def to_dto(self) -> CreateBookInput:
        return CreateBookInput(**self.model_dump())


class UpdateBookRequest(BaseModel):
    """部分更新 (PATCH)。送られた項目だけ更新する。"""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    isbn: str | None = None
    total_pages: int | None = Field(default=None, gt=0)
    current_page: int | None = Field(default=None, ge=0)
    status: ReadingStatus | None = None
    purchased_at: date | None = None
    memo: str | None = None

    def to_dto(self) -> UpdateBookInput:
        return UpdateBookInput(**self.model_dump(exclude_unset=True))
