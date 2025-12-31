"""
FastAPI application entry point.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging
from backend.app.core.middleware import RequestLoggingMiddleware

# Setup logging
log_level = "DEBUG" if settings.DEBUG else "INFO"
setup_logging(log_level=log_level, log_file="logs/app.log")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PRD助手 API",
    description="AI-powered PRD writing assistant for product managers",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Application started in {'DEBUG' if settings.DEBUG else 'PRODUCTION'} mode")
logger.info(f"CORS origins: {settings.cors_origins_list}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "PRD助手 API is running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "not_configured_yet",
        "gemini_api": "not_configured_yet",
    }


# Import and include API routers
from backend.app.api import projects, files, knowledge, conversations, export, prd, search, ai_models, wireframes, ai_test
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(prd.router, prefix="/api/prd", tags=["prd"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(ai_models.router, prefix="/api/ai", tags=["ai-models"])
app.include_router(ai_test.router)  # AI testing endpoint
app.include_router(wireframes.router, prefix="/api", tags=["wireframes"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        timeout_keep_alive=180,  # 保持连接超时 3 分钟
    )

