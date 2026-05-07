import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Ds2apiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("DS2API_KEY", "DS2API_KEY")
        self.model = model or os.getenv("DS2API_MODEL", "deepseek-ai/deepseek-v3")
        self.base_url = os.getenv("DS2API_BASE_URL", "http://localhost:6011/v1")
        
        if not self.api_key:
            raise ValueError("DS2API_KEY must be set in environment or passed to constructor")

    async def complete_with_image(self, image_base64: str, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
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
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

ds2api_client = Ds2apiClient()

def get_ds2api_client() -> Ds2apiClient:
    return ds2api_client
