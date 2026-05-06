import os
import csv
import glob
import aiofiles
import aioboto3
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

from app.schemas.cloudflare import UploadS3Response

load_dotenv()

DOWNLOAD_DIR = "download"
CSV_FILE = os.path.join(DOWNLOAD_DIR, "upload_status.csv")
S3_KEY_PREFIX = "books"

CSV_HEADERS = ["filename", "s3_key", "status", "uploaded_at", "error"]

# --- AWS Credential Resolution ---

async def _get_aws_credentials() -> dict[str, str]:
    """Fetch AWS credentials from environment variables."""
    keys = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "AWS_S3_BUCKET_NAME"]
    credentials: dict[str, str] = {}
    
    for key in keys:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required AWS credential '{key}' not found in environment variables")
        credentials[key] = value
            
    return credentials

# --- CSV Management ---

def _read_csv_statuses() -> dict[str, dict]:
    """Read the upload status CSV into a dict keyed by filename."""
    statuses: dict[str, dict] = {}
    if not os.path.exists(CSV_FILE):
        return statuses

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            statuses[row["filename"]] = row

    return statuses


def _write_csv_statuses(statuses: dict[str, dict]) -> None:
    """Write the full statuses dict back to CSV."""
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in statuses.values():
            writer.writerow(row)


def _update_csv_entry(
    statuses: dict[str, dict],
    filename: str,
    s3_key: str,
    status: str,
    error: str = "",
) -> None:
    """Update or insert a single entry in the statuses dict."""
    statuses[filename] = {
        "filename": filename,
        "s3_key": s3_key,
        "status": status,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": error,
    }

# --- Core Upload Logic ---

async def upload_book_images_to_s3(book_id: Optional[int] = None) -> UploadS3Response:
    """
    Scan the download/ folder for .jpg files, upload each to S3,
    and track status in a CSV file.
    
    Args:
        book_id: If provided, only upload files matching book_{book_id}_page_*.jpg
    """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Resolve AWS credentials from config table
    credentials = await _get_aws_credentials()
    aws_access_key = credentials["AWS_ACCESS_KEY_ID"]
    aws_secret_key = credentials["AWS_SECRET_ACCESS_KEY"]
    aws_region = credentials["AWS_REGION"]
    bucket_name = credentials["AWS_S3_BUCKET_NAME"]

    # Determine file pattern
    if book_id is not None:
        pattern = os.path.join(DOWNLOAD_DIR, f"book_{book_id}_page_*.jpg")
    else:
        pattern = os.path.join(DOWNLOAD_DIR, "*.jpg")

    files = sorted(glob.glob(pattern))

    # Load existing CSV statuses
    statuses = _read_csv_statuses()

    total_files = len(files)
    uploaded = 0
    skipped = 0
    failed = 0

    # Create aioboto3 session with decrypted credentials
    session = aioboto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region,
    )

    async with session.client("s3") as s3_client:
        for file_path in files:
            filename = os.path.basename(file_path)
            s3_key = f"{S3_KEY_PREFIX}/{filename}"

            # Skip if already uploaded
            existing = statuses.get(filename)
            if existing and existing.get("status") == "uploaded":
                skipped += 1
                continue

            # Upload to S3
            try:
                async with aiofiles.open(file_path, "rb") as f:
                    file_data = await f.read()

                await s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=file_data,
                    ContentType="image/jpeg",
                )

                _update_csv_entry(statuses, filename, s3_key, "uploaded")
                uploaded += 1
            except Exception as e:
                _update_csv_entry(statuses, filename, s3_key, "failed", str(e))
                failed += 1

    # Persist CSV
    _write_csv_statuses(statuses)

    return UploadS3Response(
        total_files=total_files,
        uploaded=uploaded,
        skipped=skipped,
        failed=failed,
    )
