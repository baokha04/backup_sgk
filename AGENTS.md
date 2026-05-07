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
  - `books.py`: Books proxy endpoints.
  - `book_pages.py`: Book pages proxy endpoints.
  - `configs.py`: Configs proxy endpoints, including `findByKey`.
  - `ocr.py`: OCR processes and fails proxy endpoints.
  - `crawl.py`: Crawler trigger proxy endpoints.
- **`app/services/`**: 
  - `cloudflare_client.py`: An asynchronous HTTP wrapper (`CloudflareClient`) using `httpx` to handle all communication with `https://sgkviet.baokha1.workers.dev`.
- **`app/schemas/`**: 
  - `cloudflare.py`: Pydantic models mapping directly to the Cloudflare Worker OpenAPI schema (e.g., `Book`, `Config`, `OcrProcess`).
- **`app/utils/`**:
  - `openrouter_client.py`: Client for OpenRouter AI vision models.
  - `mimo_client.py`: Client for Xiaomi MiMo AI vision models.


### Database
This project **does not** manage a direct database connection. All data persistence is managed remotely via the Cloudflare Worker's D1 database.

---

## 3. Code Style & Conventions

- **Typing**: Strict type hints (`typing.List`, `typing.Optional`) are expected across all function signatures and Pydantic models.
- **Async Patterns**: Endpoints and the HTTP client must use `async`/`await`. Avoid blocking synchronous I/O operations.
- **Dependency Injection**: FastAPI's `Depends` is used to inject the `CloudflareClient` instance into the route handlers.
- **Environment Variables**: Managed via `python-dotenv` and the `.env` file. Ensure all sensitive data relies on `os.getenv`.
- **Pydantic**: Use `BaseModel` for validation and schema definition. Responses should rigorously use `response_model` decorators.
- **Image Processing**: Image-to-markdown OCR includes an automated resizing step (800x1124) using `Pillow` before processing.

---

## 4. Architecture Workflow Diagram

```mermaid
graph TD
    %% Actors and Entry Points
    Client([Client / Frontend]) -->|HTTP REST| FastAPI[FastAPI Proxy Server]
    
    %% Internal Proxy Architecture
    subgraph FastAPI Proxy Application
        FastAPI --> API_Routers[Routers: /books, /configs, /ocr, etc.]
        API_Routers --> |Depends| OCR_Service[OCR Service]
        OCR_Service --> |Resizes 800x1124| ImageProc[Pillow Resizing]
        ImageProc --> |Toggle| ProviderSelection{OCR Provider?}
        ProviderSelection -->|openrouter| OR_Client[OpenRouterClient]
        ProviderSelection -->|mimo| MiMo_Client[MimoClient]
        API_Routers -.-> |Validates| Schemas[Pydantic Schemas]
    end
    
    %% External Services
    subgraph External Infrastructure
        OR_Client -->|HTTP| OR_API[OpenRouter API]
        MiMo_Client -->|HTTP| MiMo_API[Xiaomi MiMo API]
        MiMo_API -.-> CF_Worker
        OR_API -.-> CF_Worker
        CF_Worker[Cloudflare Worker API] -->|SQL| D1[(Cloudflare D1 Database)]
    end
```
