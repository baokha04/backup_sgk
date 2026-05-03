from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List
from app.schemas.cloudflare import Book, BookCreate, SuccessResponse
from app.services.cloudflare_client import CloudflareClient, get_cloudflare_client
from app.services.downloader import download_book_images

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=List[Book])
async def get_books(client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.get_books()

@router.post("/", response_model=Book, status_code=201)
async def create_book(book: BookCreate, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.create_book(book)

@router.delete("/{book_id}", response_model=SuccessResponse)
async def delete_book(book_id: int, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.delete_book(book_id)

@router.post("/{book_id}/download")
async def download_book(book_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(download_book_images, book_id)
    return {"message": f"Download task for book {book_id} has been started in the background."}

