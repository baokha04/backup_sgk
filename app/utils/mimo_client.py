import httpx
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class MimoClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("MIMO_API_KEY")
        self.model = model or os.getenv("MIMO_MODEL", "mimo-v2.5-pro")
        self.base_url = "https://api.xiaomimimo.com/v1"
        
        if not self.api_key:
            # We don't raise error here to allow other clients to work if MIMO is not used
            pass

    async def complete_with_image(self, image_base64: str, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("MIMO_API_KEY must be set to use MimoClient")

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
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
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

mimo_client = MimoClient()

def get_mimo_client() -> MimoClient:
    return mimo_client
