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
  - `crypto_helper.py`: 3DES encryption/decryption utilities using `pycryptodome` (mirrors Node.js `crypto` behavior). *Note: Currently decoupled from `configs.py` per recent changes, but available for ad-hoc encryption.*

### Database
This project **does not** manage a direct database connection. All data persistence is managed remotely via the Cloudflare Worker's D1 database.

---

## 3. Code Style & Conventions

- **Typing**: Strict type hints (`typing.List`, `typing.Optional`) are expected across all function signatures and Pydantic models.
- **Async Patterns**: Endpoints and the HTTP client must use `async`/`await`. Avoid blocking synchronous I/O operations.
- **Dependency Injection**: FastAPI's `Depends` is used to inject the `CloudflareClient` instance into the route handlers.
- **Environment Variables**: Managed via `python-dotenv` and the `.env` file (e.g., `ENCRYPTION_KEY`). Ensure all sensitive data relies on `os.getenv`.
- **Pydantic**: Use `BaseModel` for validation and schema definition. Responses should rigorously use `response_model` decorators.

---

## 4. Architecture Workflow Diagram

```mermaid
graph TD
    %% Actors and Entry Points
    Client([Client / Frontend]) -->|HTTP REST| FastAPI[FastAPI Proxy Server]
    
    %% Internal Proxy Architecture
    subgraph FastAPI Proxy Application
        FastAPI --> API_Routers[Routers: /books, /configs, /ocr, etc.]
        API_Routers --> |Depends| CF_Client[CloudflareClient / HTTPX]
        API_Routers -.-> |Validates| Schemas[Pydantic Schemas]
        CF_Client -.-> |Optionally uses| Crypto[app/utils/crypto_helper.py]
    end
    
    %% External Services
    subgraph External Infrastructure
        CF_Client -->|Async HTTP| CF_Worker[Cloudflare Worker API]
        CF_Worker -->|SQL| D1[(Cloudflare D1 Database)]
    end
```
