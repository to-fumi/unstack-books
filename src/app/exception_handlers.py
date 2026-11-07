from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from domain.exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    DomainError,
    DomainValidationError,
)


class ErrorResponse(BaseModel):
    detail: str


class ConflictResponse(ErrorResponse):
    existing_book_id: UUID | None


@dataclass(frozen=True, slots=True)
class _ErrorSpec:
    status_code: int
    model: type[ErrorResponse]
    description: str
    to_body: Callable[[Any], ErrorResponse]


def _detail_only(exc: DomainError) -> ErrorResponse:
    return ErrorResponse(detail=str(exc))


# ドメイン例外 → HTTP の対応はここだけで定義する（ハンドラと OpenAPI の両方がこれを参照する）
_ERROR_SPECS: dict[type[DomainError], _ErrorSpec] = {
    BookNotFoundError: _ErrorSpec(
        status_code=status.HTTP_404_NOT_FOUND,
        model=ErrorResponse,
        description="本が見つからない",
        to_body=_detail_only,
    ),
    BookAlreadyExistsError: _ErrorSpec(
        status_code=status.HTTP_409_CONFLICT,
        model=ConflictResponse,
        description="同じ ISBN の本がすでに登録されている",
        to_body=lambda exc: ConflictResponse(
            detail=str(exc), existing_book_id=exc.existing_book_id
        ),
    ),
    DomainValidationError: _ErrorSpec(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        model=ErrorResponse,
        description="ドメインルール違反",
        to_body=_detail_only,
    ),
}


def error_responses(*exc_types: type[DomainError]) -> dict[int | str, dict[str, Any]]:
    """ルーターの `responses=` に渡す OpenAPI 定義。エンドポイントが起こしうる例外を並べる。"""
    return {
        spec.status_code: {"model": spec.model, "description": spec.description}
        for spec in (_ERROR_SPECS[t] for t in exc_types)
    }


def register_exception_handlers(app: FastAPI) -> None:
    for exc_type, spec in _ERROR_SPECS.items():

        async def handler(_: Request, exc: Exception, spec: _ErrorSpec = spec) -> JSONResponse:
            return JSONResponse(
                status_code=spec.status_code, content=spec.to_body(exc).model_dump(mode="json")
            )

        app.add_exception_handler(exc_type, handler)
