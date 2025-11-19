"""Web scraper API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ScraperStartRequest(BaseModel):
    """Request to start scraping"""
    url: str
    max_depth: Optional[int] = 2
    respect_robots: Optional[bool] = True
    output_path: Optional[str] = None


@router.post("/start")
async def start_scraping(request: ScraperStartRequest):
    """Start scraping a website"""
    return {
        "status": "started",
        "scrape_id": "scrape-001",
        "url": request.url
    }


@router.get("/status/{scrape_id}")
async def get_scraper_status(scrape_id: str):
    """Get scraper status"""
    return {
        "scrape_id": scrape_id,
        "status": "idle",
        "progress": 0,
        "pages_scraped": 0
    }


@router.post("/stop/{scrape_id}")
async def stop_scraping(scrape_id: str):
    """Stop a scraping task"""
    return {
        "status": "stopped",
        "scrape_id": scrape_id
    }

