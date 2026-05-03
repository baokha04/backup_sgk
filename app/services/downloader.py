import os
import httpx
import aiofiles
from datetime import datetime

from app.services.cloudflare_client import get_cloudflare_client

DOWNLOAD_DIR = "download"
LOG_FILE = os.path.join(DOWNLOAD_DIR, "download.log")

async def log_download(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    async with aiofiles.open(LOG_FILE, mode='a', encoding='utf-8') as f:
        await f.write(log_line)

async def download_book_images(book_id: int, limit: int = None):
    # Ensure download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    await log_download(f"Starting download for book_id: {book_id}")
    
    try:
        client = get_cloudflare_client()
        pages = await client.get_book_pages(book_id=book_id)
        
        if limit is not None:
            pages = pages[:limit]
            
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            for page in pages:
                if not page.image_url:
                    await log_download(f"Skipped page {page.page_number} (No image_url)")
                    continue
                
                filename = f"book_{book_id}_page_{page.page_number}.jpg"
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                
                if os.path.exists(file_path):
                    await log_download(f"Skipped {filename} (File already exists)")
                    continue
                
                # Download file
                try:
                    await log_download(f"Downloading {page.image_url} to {filename}...")
                    async with http_client.stream("GET", page.image_url) as response:
                        response.raise_for_status()
                        async with aiofiles.open(file_path, 'wb') as f:
                            async for chunk in response.aiter_bytes():
                                await f.write(chunk)
                    await log_download(f"Successfully downloaded {filename}")
                except Exception as e:
                    await log_download(f"Failed to download {filename}: {str(e)}")
                    
        await log_download(f"Finished download for book_id: {book_id}")
    except Exception as e:
        await log_download(f"Critical error during download for book_id {book_id}: {str(e)}")
