import httpx
import os
import base64
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_KEY")
        self.model = model or os.getenv("AI_MODEL", "google/gemma-4-31b-it:free")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_KEY must be set in environment or passed to constructor")

    async def complete_with_image(self, image_base64: str, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/baokha04/backup_sgk", # Optional
            "X-Title": "SGKViet Backup", # Optional
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

openrouter_client = OpenRouterClient()

def get_openrouter_client() -> OpenRouterClient:
    return openrouter_client
