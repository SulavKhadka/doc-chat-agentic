"""
API routes initialization
"""

from app.api.routes.scraper import scraper_router
from app.api.routes.chat import router as chat_router

__all__ = ["scraper_router", "chat_router"] 