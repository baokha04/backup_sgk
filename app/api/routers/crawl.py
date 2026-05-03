from fastapi import APIRouter, Depends
from app.schemas.cloudflare import CrawlRequest, CrawlResponse
from app.services.cloudflare_client import CloudflareClient, get_cloudflare_client

router = APIRouter(prefix="/crawl", tags=["Crawl"])

@router.post("/", response_model=CrawlResponse)
async def crawl_book(request: CrawlRequest, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.crawl_book(request)
