"""
Workana Scraper and Dashboard Application
Main entry point for the unified FastAPI application.
"""
import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.config import config
from src.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise

# Create FastAPI application
app = FastAPI(
    title="Workana Scraper & Dashboard",
    description="Unified application for Workana project scraping and dashboard visualization",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router)

# Frontend serving
frontend_dir = Path(__file__).parent / "frontend" / "dist"

if frontend_dir.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend."""
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/{path:path}")
    async def serve_frontend_files(path: str):
        """Serve frontend files or fallback to index.html for SPA routing."""
        file_path = frontend_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Fallback to index.html for SPA routing
        return FileResponse(str(frontend_dir / "index.html"))

else:
    logger.warning("Frontend dist directory not found. Only API endpoints will be available.")

    @app.get("/")
    async def root():
        """Root endpoint when frontend is not available."""
        return {
            "message": "Workana Scraper API",
            "status": "running",
            "note": "Frontend not built yet. Visit /api/docs for API documentation."
        }

if __name__ == "__main__":
    logger.info(f"Starting Workana Scraper application on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )