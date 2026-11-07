from fastapi import APIRouter

from controller.routers import books

api_router = APIRouter()
api_router.include_router(books.router)
