from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import UUID4
from uuid import UUID
import logging
import asyncio
from functools import partial

logger = logging.getLogger(__name__)

from app.models.scraper import (
    ScrapeRequest,
    ScrapeResponse,
    URLEntry
)
from app.services.scraper import ScraperService
from app.api.dependencies import get_scraper_service

scraper_router = APIRouter()

@scraper_router.post("/url")
async def scrape_url(
    request: ScrapeRequest,
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """
    Scrape a URL and store its content
    """
    try:
        response = await scraper_service.scrape_url(request)
        return response
    except Exception as e:
        logger.error(f"Error processing scrape request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@scraper_router.get("/content/{url_id}", response_model=URLEntry)
async def get_url_content(
    url_id: UUID4,
    scraper_service: ScraperService = Depends(get_scraper_service)
) -> URLEntry:
    """
    Get the scraped content for a specific URL.
    """
    url_entry = scraper_service.get_url_content(url_id)
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL entry not found")
    return url_entry

@scraper_router.get("/conversation/{conversation_id}", response_model=List[URLEntry])
async def get_conversation_urls(
    conversation_id: str,
    scraper_service: ScraperService = Depends(get_scraper_service)
) -> List[URLEntry]:
    """
    Get all URLs associated with a specific conversation.
    """
    return scraper_service.get_conversation_urls(conversation_id)
