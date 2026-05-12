from fastapi import APIRouter, Depends
from typing import List, Optional
from app.schemas.cloudflare import (
    OcrProcess, OcrProcessCreate, 
    OcrFail, OcrFailCreate, 
    OcrBatchResponse, SuccessResponse
)
from app.services.cloudflare_client import CloudflareClient, get_cloudflare_client
from app.services.ocr_service import OCRService, get_ocr_service

process_router = APIRouter(prefix="/ocr_processes", tags=["OCR Processes"])

@process_router.get("/", response_model=List[OcrProcess])
async def get_ocr_processes(client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.get_ocr_processes()

@process_router.post("/", response_model=OcrProcess, status_code=201)
async def create_ocr_process(process: OcrProcessCreate, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.create_ocr_process(process)

@process_router.put("/{process_id}", response_model=OcrProcess)
async def update_ocr_process(process_id: int, process: OcrProcessCreate, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.update_ocr_process(process_id, process)

@process_router.delete("/{process_id}", response_model=SuccessResponse)
async def delete_ocr_process(process_id: int, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.delete_ocr_process(process_id)

@process_router.post("/process-batch", response_model=OcrBatchResponse)
async def process_ocr_batch(client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.process_ocr_batch()

@process_router.post("/process-book/{book_id}", response_model=OcrBatchResponse)
async def process_book_ocr(book_id: int, service: OCRService = Depends(get_ocr_service)):
    return await service.process_book_ocr(book_id)

@process_router.post("/process-page/{page_id}", response_model=Optional[str])
async def process_page_ocr(page_id: int, client: CloudflareClient = Depends(get_cloudflare_client), service: OCRService = Depends(get_ocr_service)):
    # Fetch page info from Cloudflare
    pages = await client.get_book_pages()
    page = next((p for p in pages if p.id == page_id), None)
    if not page:
        return None
    return await service.process_page_ocr(page)


fail_router = APIRouter(prefix="/ocr_fails", tags=["OCR Fails"])

@fail_router.get("/", response_model=List[OcrFail])
async def get_ocr_fails(client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.get_ocr_fails()

@fail_router.post("/", response_model=OcrFail, status_code=201)
async def create_ocr_fail(fail: OcrFailCreate, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.create_ocr_fail(fail)

@fail_router.delete("/{fail_id}", response_model=SuccessResponse)
async def delete_ocr_fail(fail_id: int, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.delete_ocr_fail(fail_id)
