import os
import base64
import logging
import asyncio
import httpx
from typing import List, Optional
import io
from typing import List, Optional, Any
from PIL import Image
from app.services.cloudflare_client import CloudflareClient, get_cloudflare_client
from app.utils.openrouter_client import OpenRouterClient, get_openrouter_client
from app.utils.mimo_client import MimoClient, get_mimo_client
from app.utils.ds2api_client import Ds2apiClient, get_ds2api_client
from app.utils.ai_hay_client import AiHayClient, get_ai_hay_client
from app.schemas.cloudflare import OcrProcessCreate, OcrFailCreate, BookPage, OcrBatchResponse

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(
        self, 
        cf_client: Optional[CloudflareClient] = None,
        vision_client: Optional[Any] = None,
        download_dir: str = "download"
    ):
        self.cf_client = cf_client or get_cloudflare_client()
        self.vision_client = vision_client or self._get_default_vision_client()
        self.download_dir = download_dir
        self.lock = asyncio.Lock()

    def _get_default_vision_client(self):
        provider = os.getenv("OCR_PROVIDER", "mimo").lower()
        if provider == "mimo":
            return get_mimo_client()
        if provider == "ds2api":
            return get_ds2api_client()
        if provider == "ai_hay":
            return get_ai_hay_client()
        return get_openrouter_client()

    def _get_image_path(self, book_id: int, page_number: int) -> str:
        return os.path.join(self.download_dir, f"book_{book_id}_page_{page_number}.jpg")

    def _encode_image(self, image_path: str) -> str:
        """Resize image to 1240x1754 and encode to base64."""
        with Image.open(image_path) as img:
            # Resize image
            resized_img = img.resize((1240, 1754), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (e.g. for PNG/RGBA)
            if resized_img.mode in ("RGBA", "P"):
                resized_img = resized_img.convert("RGB")
                
            # Save to buffer
            buffer = io.BytesIO()
            resized_img.save(buffer, format="JPEG", quality=95)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')

    async def process_page_ocr(self, page: BookPage) -> Optional[str]:
        """Process OCR for a single page."""
        image_path = self._get_image_path(page.book_id, page.page_number)
        
        if not os.path.exists(image_path):
            logger.warning(f"Image not found: {image_path}")
            return None

        print(f"Processing OCR for Book {page.book_id} Page {page.page_number}...")
        
        try:
            image_base64 = self._encode_image(image_path)
            prompt = (
                "Please perform high-fidelity OCR on this image and convert the content into structured Markdown format. "
                "The content contains Vietnamese, so pay close attention to diacritics and special characters to ensure 100% accuracy in spelling.\n"
                "Requirements:\n"
                "- Maintain the original hierarchy of headings (using #, ##, ###).\n"
                "- Reconstruct all tables accurately using Markdown table syntax.\n"
                "- Preserve text styles such as bold, italics, and lists (bulleted or numbered).\n"
                "- If there are any mathematical formulas or technical symbols, render them in LaTeX.\n"
                "- Output the final result in clean Markdown code. Do not summarize or omit any information."
            )
            
            # Global lock to ensure sequential processing and avoid 429s
            async with self.lock:
                max_retries = 5
                retry_delay = 10
                
                for attempt in range(max_retries):
                    try:
                        markdown = await self.vision_client.complete_with_image(image_base64, prompt)
                        break
                    except httpx.HTTPStatusError as e:
                        # Retry on rate limits (429) or transient server errors (5xx)
                        status_code = e.response.status_code
                        if (status_code == 429 or 500 <= status_code < 600) and attempt < max_retries - 1:
                            logger.warning(f"Received {status_code} error. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2 # Exponential backoff
                            continue
                        raise e
            
            # 1. Upsert OCR Process
            process_req = OcrProcessCreate(
                book_page_id=page.id,
                markdown=markdown,
                status="success"
            )
            ocr_process = await self.cf_client.upsert_ocr_process(process_req)
            
            # 2. Update Book Page with ocr_process_id
            await self.cf_client.update_book_page_ocr_process(page.id, ocr_process.id)
            
            print(f"OCR completed and saved for Page {page.id} (Process ID: {ocr_process.id})")
            return markdown
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing OCR for page {page.id}: {error_msg}")
            
            # Record failure in ocr_fails table
            try:
                fail_req = OcrFailCreate(
                    book_page_id=page.id,
                    reason=error_msg
                )
                await self.cf_client.create_ocr_fail(fail_req)
                print(f"Recorded OCR failure for Page {page.id}")
            except Exception as fe:
                logger.error(f"Failed to record OCR failure for page {page.id}: {str(fe)}")
                
            return None

    async def process_book_ocr(self, book_id: int) -> OcrBatchResponse:
        """Process OCR for all pages of a book that don't have an OCR process ID."""
        pages = await self.cf_client.get_book_pages(book_id=book_id)
        
        processed_pages = 0
        success_count = 0
        failure_count = 0
        
        for page in pages:
            if page.ocr_process_id is not None:
                print(f"Skipping Page {page.page_number} (ID: {page.id}) - already processed (Process ID: {page.ocr_process_id})")
                continue
                
            processed_pages += 1
            res = await self.process_page_ocr(page)
            if res:
                success_count += 1
            else:
                failure_count += 1
            
            # Additional sleep to avoid rate limits during batch processing
            await asyncio.sleep(10)
                
        return OcrBatchResponse(
            processed_pages=processed_pages,
            success_count=success_count,
            failure_count=failure_count
        )

ocr_service = OCRService()

def get_ocr_service() -> OCRService:
    return ocr_service
