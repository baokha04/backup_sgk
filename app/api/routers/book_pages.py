from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.cloudflare import BookPage, BookPageCreate, SuccessResponse
from app.services.cloudflare_client import CloudflareClient, get_cloudflare_client

router = APIRouter(prefix="/book_pages", tags=["Book Pages"])

@router.get("/", response_model=List[BookPage])
async def get_book_pages(
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
    from_page: Optional[int] = Query(None, description="Filter from page number (inclusive)"),
    to_page: Optional[int] = Query(None, description="Filter to page number (inclusive)"),
    client: CloudflareClient = Depends(get_cloudflare_client)
):
    return await client.get_book_pages(book_id=book_id, from_page=from_page, to_page=to_page)

@router.post("/", response_model=BookPage, status_code=201)
async def create_book_page(page: BookPageCreate, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.create_book_page(page)

@router.delete("/{page_id}", response_model=SuccessResponse)
async def delete_book_page(page_id: int, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.delete_book_page(page_id)
