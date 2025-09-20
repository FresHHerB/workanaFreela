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
    logger.info(f"Config - HOST: {config.HOST}, PORT: {config.PORT}, DEBUG: {config.DEBUG}")
    logger.info(f"Config - WORKANA_EMAIL: {'SET' if config.WORKANA_EMAIL else 'MISSING'}")
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    # Don't crash immediately, show debug info
    logger.error(f"Environment debug - HOST: {config.HOST}, PORT: {config.PORT}")
    logger.error(f"Environment debug - WORKANA_EMAIL: {'SET' if config.WORKANA_EMAIL else 'MISSING'}")
    logger.error(f"Environment debug - WORKANA_PASSWORD: {'SET' if config.WORKANA_PASSWORD else 'MISSING'}")
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
logger.info(f"Looking for frontend at: {frontend_dir}")
logger.info(f"Frontend directory exists: {frontend_dir.exists()}")

if frontend_dir.exists():
    # Check assets directory
    assets_dir = frontend_dir / "assets"
    index_file = frontend_dir / "index.html"

    logger.info(f"Assets directory exists: {assets_dir.exists()}")
    logger.info(f"Index.html exists: {index_file.exists()}")

    if assets_dir.exists():
        # Mount static assets
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        logger.info("Static assets mounted at /assets")

    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend."""
        logger.info(f"Serving frontend from: {index_file}")
        return FileResponse(str(index_file))

    @app.get("/{path:path}")
    async def serve_frontend_files(path: str):
        """Serve frontend files or fallback to index.html for SPA routing."""
        file_path = frontend_dir / path
        if file_path.exists() and file_path.is_file():
            logger.debug(f"Serving file: {file_path}")
            return FileResponse(str(file_path))
        # Fallback to index.html for SPA routing
        logger.debug(f"Fallback to index.html for path: {path}")
        return FileResponse(str(index_file))

    logger.info("Frontend serving configured successfully")

else:
    logger.warning(f"Frontend dist directory not found at: {frontend_dir}")
    logger.warning("Only API endpoints will be available.")

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