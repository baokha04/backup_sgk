import os
import base64
import logging
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
import tempfile
import random
from typing import Optional, List
from playwright.async_api import async_playwright, BrowserContext, Page
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]

VIEWPORTS = [
    {'width': 1280, 'height': 800},
    {'width': 1366, 'height': 768},
    {'width': 1440, 'height': 900},
    {'width': 1536, 'height': 864},
    {'width': 1920, 'height': 1080},
]

SESSION_DIR = os.path.join(os.getcwd(), "sessions")
SESSION_FILE = os.path.join(SESSION_DIR, "ai_hay_session.json")

class AiHayClient:
    """Enhanced Browser-automation client for ai-hay.vn OCR."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        if not os.path.exists(SESSION_DIR):
            os.makedirs(SESSION_DIR)

    async def _random_sleep(self, min_s: float = 1.0, max_s: float = 3.0):
        await asyncio.sleep(random.uniform(min_s, max_s))

    def _get_random_ua(self) -> str:
        return random.choice(USER_AGENTS)

    def _get_random_viewport(self) -> dict:
        return random.choice(VIEWPORTS)

    async def _setup_context(self, browser) -> BrowserContext:
        ua = self._get_random_ua()
        viewport = self._get_random_viewport()
        
        # Hardware randomization
        hardware_concurrency = random.choice([4, 8, 12, 16])
        device_memory = random.choice([4, 8, 16])

        logger.info(f"Creating browser context with UA: {ua} and Viewport: {viewport}")
        
        storage_state = SESSION_FILE if os.path.exists(SESSION_FILE) else None
        
        context = await browser.new_context(
            user_agent=ua,
            viewport=viewport,
            storage_state=storage_state,
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh",
            device_scale_factor=random.choice([1, 2]),
            has_touch=random.choice([True, False]),
        )

        # Add hardware fingerprinting scripts
        await context.add_init_script(f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {hardware_concurrency} }});
            Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {device_memory} }});
            Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
        """)

        return context

    async def complete_with_image(self, image_base64: str, prompt: str) -> str:
        """
        Processes an image for OCR via ai-hay.vn using enhanced browser automation.
        """
        loop = asyncio.get_running_loop()
        logger.info(f"AiHayClient using event loop: {type(loop)}")
        if sys.platform == 'win32' and 'Proactor' not in str(type(loop)):
            logger.warning("WARNING: Not using ProactorEventLoop on Windows. Subprocesses (Playwright) may fail with NotImplementedError.")

        temp_file_path = None
        try:
            # 1. Save base64 image to temp file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                image_data = base64.b64decode(image_base64)
                tmp.write(image_data)
                temp_file_path = tmp.name

            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await self._setup_context(browser)
                page = await context.new_page()
                
                # Stealth is automatically applied by Stealth().use_async()
                # No need for manual call anymore

                logger.info("Navigating to https://ai-hay.vn/ ...")
                await page.goto("https://ai-hay.vn/", wait_until="networkidle")
                await self._random_sleep(2, 4)

                # 2. Upload image
                logger.info(f"Uploading image to AI Hay: {temp_file_path}")
                file_input = page.locator("input[type='file']")
                await file_input.set_input_files(temp_file_path)
                
                # Wait for upload to register
                await self._random_sleep(3, 5)

                # 3. Type prompt (with human-like typing)
                textarea = page.locator("textarea[placeholder*='Hỏi mình']").first
                await textarea.click()
                await textarea.type(prompt, delay=random.uniform(30, 80))
                await self._random_sleep(1, 2)

                # 4. Send
                await textarea.press("Enter")
                logger.info("Message sent! Waiting for response...")

                # 5. Wait for response to stabilize
                last_text = ""
                stable_count = 0
                max_retries = 40 # ~120s
                
                for i in range(max_retries):
                    await asyncio.sleep(3)
                    
                    # Extract last response block
                    current_text = await page.evaluate("""() => {
                        const messages = document.querySelectorAll('.prose, [class*="message"], [class*="response"], [class*="markdown"]');
                        if (messages.length === 0) return "";
                        return messages[messages.length - 1].innerText;
                    }""")
                    
                    if current_text:
                        if current_text == last_text and len(current_text) > 10:
                            stable_count += 1
                            if stable_count >= 3:
                                logger.info("Response stabilized.")
                                # Save session state before closing
                                await context.storage_state(path=SESSION_FILE)
                                break
                        else:
                            stable_count = 0
                            if i % 5 == 0:
                                logger.info(f"Response growing... ({len(current_text)} chars)")
                        
                        last_text = current_text

                await browser.close()
                return last_text

        except Exception as e:
            logger.error(f"Error in AiHayClient: {str(e)}")
            raise
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

def get_ai_hay_client():
    return AiHayClient()
