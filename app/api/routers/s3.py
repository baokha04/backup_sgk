from fastapi import APIRouter, Query
from typing import Optional

from app.schemas.cloudflare import UploadS3Response
from app.services.s3_uploader import upload_book_images_to_s3

router = APIRouter(prefix="/s3", tags=["S3"])

@router.post("/upload", response_model=UploadS3Response)
async def upload_to_s3(book_id: Optional[int] = Query(None, description="Filter by book_id")):
    """Upload images from the download folder to the S3 bucket."""
    return await upload_book_images_to_s3(book_id=book_id)
