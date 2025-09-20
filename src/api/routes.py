"""
API routes for the Workana Scraper application.
"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..services import scraper

logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter(prefix="/api")

@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "workana-scraper"}

@api_router.get("/debug")
async def debug_info():
    """Debug endpoint to check application state."""
    from pathlib import Path
    import os

    frontend_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"

    return {
        "status": "running",
        "frontend": {
            "dist_dir_exists": frontend_dir.exists(),
            "dist_dir_path": str(frontend_dir),
            "index_html_exists": (frontend_dir / "index.html").exists(),
            "assets_dir_exists": (frontend_dir / "assets").exists(),
        },
        "environment": {
            "WORKANA_EMAIL": "SET" if os.getenv("WORKANA_EMAIL") else "MISSING",
            "WORKANA_PASSWORD": "SET" if os.getenv("WORKANA_PASSWORD") else "MISSING",
            "PORT": os.getenv("PORT", "8000"),
            "HOST": os.getenv("HOST", "0.0.0.0"),
            "DEBUG": os.getenv("DEBUG", "false"),
        },
        "paths": {
            "current_dir": str(Path.cwd()),
            "app_dir": str(Path(__file__).parent.parent.parent),
        }
    }

@api_router.get("/scrape")
async def scrape_workana():
    """
    Scrape Workana projects.

    Returns:
        JSON response with scraped project data or error information.
    """
    try:
        result = await scraper.scrape_projects()

        if result["status"] == "success":
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Unknown error occurred")
            )

    except Exception as e:
        logger.error(f"API error in scrape endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )