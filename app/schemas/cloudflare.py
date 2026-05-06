from typing import Optional
from pydantic import BaseModel

class Book(BaseModel):
    id: Optional[int] = None
    title: str
    unsigned_title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    total_pages: Optional[int] = None
    deleted: Optional[bool] = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BookCreate(BaseModel):
    title: str
    unsigned_title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    total_pages: Optional[int] = None

class Config(BaseModel):
    id: Optional[int] = None
    key: str
    value: Optional[str] = None
    active: Optional[bool] = True
    deleted: Optional[bool] = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ConfigCreate(BaseModel):
    key: str
    value: Optional[str] = None
    active: Optional[bool] = True

class BookPage(BaseModel):
    id: Optional[int] = None
    book_id: int
    page_number: int
    image_url: Optional[str] = None
    html_content: Optional[str] = None
    ocr_process_id: Optional[int] = None
    deleted: Optional[bool] = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BookPageCreate(BaseModel):
    book_id: int
    page_number: int
    image_url: Optional[str] = None
    html_content: Optional[str] = None
    ocr_process_id: Optional[int] = None

class OcrProcess(BaseModel):
    id: Optional[int] = None
    book_page_id: int
    markdown: Optional[str] = None
    status: str
    deleted: Optional[bool] = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class OcrProcessCreate(BaseModel):
    book_page_id: int
    markdown: Optional[str] = None
    status: str

class OcrFail(BaseModel):
    id: Optional[int] = None
    book_page_id: Optional[int] = None
    reason: Optional[str] = None
    deleted: Optional[bool] = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class OcrFailCreate(BaseModel):
    book_page_id: Optional[int] = None
    reason: Optional[str] = None

class CrawlRequest(BaseModel):
    url: str

class CrawlResponseBook(BaseModel):
    id: int
    title: str
    total_pages: int

class CrawlResponse(BaseModel):
    book: CrawlResponseBook
    pages_inserted: int

class OcrBatchResponse(BaseModel):
    processed_pages: int
    success_count: int
    failure_count: int

class SuccessResponse(BaseModel):
    success: bool

class BookPageIdResponse(BaseModel):
    id: int

class BookPageOcrUpdate(BaseModel):
    ocr_process_id: int

class UploadS3Response(BaseModel):
    total_files: int
    uploaded: int
    skipped: int
    failed: int


