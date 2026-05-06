from fastapi import APIRouter

from app.api.routers.books import router as books_router
from app.api.routers.configs import router as configs_router
from app.api.routers.book_pages import router as book_pages_router
from app.api.routers.ocr import process_router, fail_router
from app.api.routers.crawl import router as crawl_router
from app.api.routers.s3 import router as s3_router

api_router = APIRouter()

api_router.include_router(books_router)
api_router.include_router(configs_router)
api_router.include_router(book_pages_router)
api_router.include_router(process_router)
api_router.include_router(fail_router)
api_router.include_router(crawl_router)
api_router.include_router(s3_router)
