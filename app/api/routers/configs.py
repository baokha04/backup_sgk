from fastapi import APIRouter, Depends
from typing import List

from app.schemas.cloudflare import Config, ConfigCreate, SuccessResponse
from app.services.cloudflare_client import CloudflareClient, get_cloudflare_client

router = APIRouter(prefix="/configs", tags=["Configs"])

@router.get("/", response_model=List[Config])
async def get_configs(client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.get_configs()

@router.get("/key/{key}", response_model=Config)
async def get_config_by_key(key: str, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.get_config_by_key(key)

@router.post("/", response_model=Config, status_code=201)
async def create_config(config: ConfigCreate, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.create_config(config)

@router.put("/{config_id}", response_model=Config)
async def update_config(config_id: int, config: ConfigCreate, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.update_config(config_id, config)

@router.delete("/{config_id}", response_model=SuccessResponse)
async def delete_config(config_id: int, client: CloudflareClient = Depends(get_cloudflare_client)):
    return await client.delete_config(config_id)




