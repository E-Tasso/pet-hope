from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text

from app import __version__
from app.config import get_settings
from app.database import close_db, engine
from app.services.storage import get_storage_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print("Starting PetHope API...")
    print(f"Environment: {settings.environment}")
    print(f"Database: {settings.database_url.split('@')[-1]}")  # Hide credentials

    # Initialize storage service (creates bucket if needed)
    storage = get_storage_service()
    print(f"Storage bucket: {storage.bucket}")

    yield

    # Shutdown
    print("Shutting down PetHope API...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="API for PetHope - Pet adoption platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint - redirect to docs
@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns the status of the API and its dependencies.

    Returns:
        JSONResponse with health status
    """
    health_status = {
        "status": "healthy",
        "version": __version__,
        "environment": settings.environment,
        "checks": {
            "database": "unknown",
            "storage": "unknown",
        },
    }

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check storage
    try:
        storage = get_storage_service()
        if storage.health_check():
            health_status["checks"]["storage"] = "healthy"
        else:
            health_status["checks"]["storage"] = "unhealthy: bucket not found"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["storage"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503

    return JSONResponse(content=health_status, status_code=status_code)


# Include routers
from app.routers import animals, helpers, images

app.include_router(animals.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(helpers.router, prefix="/api")
