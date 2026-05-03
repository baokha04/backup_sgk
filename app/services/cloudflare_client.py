import httpx
from typing import List, Optional, Any, Dict
from app.schemas.cloudflare import (
    Book, BookCreate, Config, ConfigCreate, BookPage, BookPageCreate,
    OcrProcess, OcrProcessCreate, OcrFail, OcrFailCreate,
    CrawlRequest, CrawlResponse, OcrBatchResponse, SuccessResponse
)

class CloudflareClient:
    def __init__(self, base_url: str = "https://sgkviet.baokha1.workers.dev"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def close(self):
        await self.client.aclose()

    async def _handle_response(self, response: httpx.Response) -> Any:
        response.raise_for_status()
        return response.json()

    # Books
    async def get_books(self) -> List[Book]:
        response = await self.client.get("/books")
        data = await self._handle_response(response)
        return [Book(**item) for item in data]

    async def create_book(self, book: BookCreate) -> Book:
        response = await self.client.post("/books", json=book.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return Book(**data)

    async def delete_book(self, book_id: int) -> SuccessResponse:
        response = await self.client.delete(f"/books/{book_id}")
        data = await self._handle_response(response)
        return SuccessResponse(**data)

    # Configs
    async def get_configs(self) -> List[Config]:
        response = await self.client.get("/configs")
        data = await self._handle_response(response)
        return [Config(**item) for item in data]

    async def get_config_by_key(self, key: str) -> Config:
        response = await self.client.get(f"/configs/key/{key}")
        data = await self._handle_response(response)
        return Config(**data)

    async def create_config(self, config: ConfigCreate) -> Config:
        response = await self.client.post("/configs", json=config.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return Config(**data)

    async def update_config(self, config_id: int, config: ConfigCreate) -> Config:
        response = await self.client.put(f"/configs/{config_id}", json=config.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return Config(**data)

    async def delete_config(self, config_id: int) -> SuccessResponse:
        response = await self.client.delete(f"/configs/{config_id}")
        data = await self._handle_response(response)
        return SuccessResponse(**data)

    # Book Pages
    async def get_book_pages(self, book_id: Optional[int] = None, from_page: Optional[int] = None, to_page: Optional[int] = None) -> List[BookPage]:
        params = {}
        if book_id is not None:
            params['book_id'] = book_id
        if from_page is not None:
            params['from_page'] = from_page
        if to_page is not None:
            params['to_page'] = to_page
            
        response = await self.client.get("/book_pages", params=params)
        data = await self._handle_response(response)
        return [BookPage(**item) for item in data]

    async def create_book_page(self, page: BookPageCreate) -> BookPage:
        response = await self.client.post("/book_pages", json=page.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return BookPage(**data)

    async def delete_book_page(self, page_id: int) -> SuccessResponse:
        response = await self.client.delete(f"/book_pages/{page_id}")
        data = await self._handle_response(response)
        return SuccessResponse(**data)

    # OCR Processes
    async def get_ocr_processes(self) -> List[OcrProcess]:
        response = await self.client.get("/ocr_processes")
        data = await self._handle_response(response)
        return [OcrProcess(**item) for item in data]

    async def create_ocr_process(self, process: OcrProcessCreate) -> OcrProcess:
        response = await self.client.post("/ocr_processes", json=process.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return OcrProcess(**data)

    async def update_ocr_process(self, process_id: int, process: OcrProcessCreate) -> OcrProcess:
        response = await self.client.put(f"/ocr_processes/{process_id}", json=process.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return OcrProcess(**data)

    async def delete_ocr_process(self, process_id: int) -> SuccessResponse:
        response = await self.client.delete(f"/ocr_processes/{process_id}")
        data = await self._handle_response(response)
        return SuccessResponse(**data)

    async def process_ocr_batch(self) -> OcrBatchResponse:
        response = await self.client.post("/ocr_processes/process-batch")
        data = await self._handle_response(response)
        return OcrBatchResponse(**data)

    # OCR Fails
    async def get_ocr_fails(self) -> List[OcrFail]:
        response = await self.client.get("/ocr_fails")
        data = await self._handle_response(response)
        return [OcrFail(**item) for item in data]

    async def create_ocr_fail(self, fail: OcrFailCreate) -> OcrFail:
        response = await self.client.post("/ocr_fails", json=fail.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return OcrFail(**data)

    async def delete_ocr_fail(self, fail_id: int) -> SuccessResponse:
        response = await self.client.delete(f"/ocr_fails/{fail_id}")
        data = await self._handle_response(response)
        return SuccessResponse(**data)

    # Crawl
    async def crawl_book(self, crawl_req: CrawlRequest) -> CrawlResponse:
        response = await self.client.post("/crawl", json=crawl_req.model_dump(exclude_unset=True))
        data = await self._handle_response(response)
        return CrawlResponse(**data)

# Dependency to get client instance
cloudflare_client = CloudflareClient()

def get_cloudflare_client() -> CloudflareClient:
    return cloudflare_client
