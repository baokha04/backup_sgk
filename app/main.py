from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.api import api_router
from app.services.cloudflare_client import get_cloudflare_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    client = get_cloudflare_client()
    await client.close()

app = FastAPI(
    title="SGKViet API (Proxy)",
    description="FastAPI service proxying the Cloudflare Worker API for SGKViet.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redistoc_url="/redoc"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the SGKViet FastAPI Proxy! View docs at /docs"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SGKViet API",
        version="1.0.0",
        description="FastAPI swagger documentation for the Cloudflare API integration.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
