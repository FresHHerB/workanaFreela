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