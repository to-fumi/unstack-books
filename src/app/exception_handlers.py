"""ドメイン例外 → HTTP レスポンスへの変換。"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import BookNotFoundError, DomainValidationError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookNotFoundError)
    async def _not_found(_: Request, exc: BookNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(DomainValidationError)
    async def _validation(_: Request, exc: DomainValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": str(exc)}
        )
