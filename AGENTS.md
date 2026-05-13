# AGENTS.md

## Project Overview
This project (`backup_sgk`) is a Python FastAPI proxy service acting as a backend intermediary for the SGKViet Cloudflare Worker API. It utilizes `httpx` for asynchronous HTTP requests to the worker and `pydantic` for data validation, exposing a unified Swagger documentation.

---

## 1. Build and Run Commands

- **Dependency Management**: Uses `uv`.
- **Install Dependencies**: `uv sync` or `uv pip install -r pyproject.toml`
- **Run Development Server**: 
  ```bash
  uv run uvicorn app.main:app --reload
  ```
- **Tests/Linting**: Currently no test framework (e.g., `pytest`) or linter (e.g., `ruff`) is explicitly configured in `pyproject.toml`. It is recommended to use `ruff check .` for linting if `ruff` is installed.

---

## 2. Architecture & Structure

### Core Components
- **`app/main.py`**: The entry point for the FastAPI application. Sets up CORS, lifespan hooks, and dynamic Swagger UI configuration.
- **`app/api/routers/`**: Contains endpoint definitions, passing requests to the client service.
  - `books.py`: Books proxy endpoints, including background image downloading.
  - `book_pages.py`: Book pages proxy endpoints.
  - `configs.py`: Configs proxy endpoints, including `findByKey`.
  - `ocr.py`: OCR processes and fails proxy endpoints, and batch processing triggers.
  - `crawl.py`: Crawler trigger proxy endpoints.
  - `s3.py`: Endpoints for uploading downloaded images to S3.
- **`app/services/`**:
  - `cloudflare_client.py`: An asynchronous HTTP wrapper (`CloudflareClient`) using `httpx` to handle all communication with the remote Cloudflare Worker API.
  - `ocr_service.py`: Orchestrates the OCR pipeline, including image encoding, provider selection, and result persistence.
  - `downloader.py`: Handles asynchronous background downloading of book images from external URLs.
  - `s3_uploader.py`: Manages uploading local images to AWS S3 with status tracking via CSV.
- **`app/schemas/`**: 
  - `cloudflare.py`: Pydantic models mapping directly to the Cloudflare Worker OpenAPI schema (e.g., `Book`, `Config`, `OcrProcess`).
- **`app/utils/`**:
  - `openrouter_client.py`: Client for OpenRouter AI vision models.
  - `mimo_client.py`: Client for Xiaomi MiMo AI vision models.
  - `ds2api_client.py`: Client for DS2 API vision models.


### Database
This project **does not** manage a direct database connection. All data persistence is managed remotely via the Cloudflare Worker's D1 database.

---

## 3. Code Style & Conventions

- **Typing**: Strict type hints (`typing.List`, `typing.Optional`) are expected across all function signatures and Pydantic models.
- **Async Patterns**: Endpoints and the HTTP client must use `async`/`await`. Avoid blocking synchronous I/O operations.
- **Dependency Injection**: FastAPI's `Depends` is used to inject service instances into the route handlers.
- **Environment Variables**: Managed via `python-dotenv` and the `.env` file. Ensure all sensitive data relies on `os.getenv`.
- **Pydantic**: Use `BaseModel` for validation and schema definition. Responses should rigorously use `response_model` decorators.
- **Image Processing**: Image-to-markdown OCR includes an automated resizing step (**1240x1754**) using `Pillow` before processing.
- **Error Handling**: `OCRService` implements a global lock to prevent rate limits (429) and uses exponential backoff for retries.

---

## 4. Architecture Workflow Diagram

```mermaid
graph TD
    %% Actors and Entry Points
    Client([Client / Frontend]) -->|HTTP REST| FastAPI[FastAPI Proxy Server]
    
    %% Internal Proxy Architecture
    subgraph FastAPI Proxy Application
        FastAPI --> API_Routers[Routers: /books, /configs, /ocr, /s3, etc.]
        
        API_Routers --> |Background Task| Downloader[Downloader Service]
        Downloader --> |Saves to| LocalDisk[(Local /download folder)]
        
        API_Routers --> |Depends| OCR_Service[OCR Service]
        OCR_Service --> |Reads from| LocalDisk
        OCR_Service --> |Resizes 1240x1754| ImageProc[Pillow Resizing]
        ImageProc --> |Toggle| ProviderSelection{OCR Provider?}
        ProviderSelection -->|openrouter| OR_Client[OpenRouterClient]
        ProviderSelection -->|mimo| MiMo_Client[MimoClient]
        ProviderSelection -->|ds2api| DS2_Client[Ds2apiClient]
        
        API_Routers --> |Triggers| S3_Uploader[S3 Uploader Service]
        S3_Uploader --> |Reads from| LocalDisk
        S3_Uploader --> |Tracks in| CSV_Status[upload_status.csv]
        
        API_Routers -.-> |Validates| Schemas[Pydantic Schemas]
    end
    
    %% External Services
    subgraph External Infrastructure
        LocalDisk -.-> |Source| Ext_URLs[External Image URLs]
        OR_Client -->|HTTP| OR_API[OpenRouter API]
        MiMo_Client -->|HTTP| MiMo_API[Xiaomi MiMo API]
        DS2_Client -->|HTTP| DS2_API[DS2 API]
        S3_Uploader -->|Boto3| AWS_S3[(AWS S3 Bucket)]
        
        API_Routers -->|HTTP Proxy| CF_Worker[Cloudflare Worker API]
        CF_Worker -->|SQL| D1[(Cloudflare D1 Database)]
    end
```
