import logging
from typing import Optional
from uuid import UUID, uuid4
from app.models.scraper import ScrapeRequest, ScrapeResponse, URLEntry, URLStatus
import json
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from app.core.config import Settings

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self, settings: Settings):
        self.settings = settings
        # Create storage directory if it doesn't exist
        self.settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.storage_path = self.settings.STORAGE_DIR / "urls.json"
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Ensure the storage directory and file exist"""
        if not self.storage_path.exists():
            # Create parent directories if they don't exist
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            # Create the file with an empty list
            with open(self.storage_path, 'w') as f:
                json.dump([], f)

    def _load_urls(self) -> list[URLEntry]:
        """Load URLs from storage"""
        try:
            if not self.storage_path.exists():
                self._ensure_storage_exists()
                return []
            
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return [URLEntry.model_validate(entry) for entry in data]
        except Exception as e:
            logger.error(f"Error loading URLs: {e}")
            return []

    def _save_urls(self, urls: list[URLEntry]):
        """Save URLs to storage"""
        try:
            # Ensure parent directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert URLs to dict and save
            with open(self.storage_path, 'w') as f:
                json.dump([url.model_dump() for url in urls], f, default=str)
        except Exception as e:
            logger.error(f"Error saving URLs: {e}", exc_info=True)
            raise

    def _get_url_entry(self, url_id: UUID) -> Optional[URLEntry]:
        """Get a specific URL entry"""
        urls = self._load_urls()
        return next((url for url in urls if str(url.id) == str(url_id)), None)

    def scrape_url(self, request: ScrapeRequest) -> ScrapeResponse:
        """Scrape a URL and store its content"""
        urls = self._load_urls()
        
        # Check if URL already exists for this conversation
        existing_url = next(
            (url for url in urls 
             if url.url == request.url and url.conversation_id == request.conversation_id),
            None
        )

        if existing_url and not request.force_refresh:
            return ScrapeResponse(url_entry=existing_url)

        # Create new URL entry or update existing one
        url_entry = existing_url or URLEntry(
            id=uuid4(),
            url=request.url,
            status=URLStatus.LOADING,
            conversation_id=request.conversation_id
        )

        try:
            # Use ScraperAPI for reliable scraping
            api_url = f"http://api.scraperapi.com?api_key={self.settings.SCRAPER_API_KEY}&url={request.url}&render=true"
            response = requests.get(api_url, timeout=60)  # Add timeout
            response.raise_for_status()

            # Save raw HTML
            html_path = self.settings.SCRAPED_CONTENT_DIR / f"{url_entry.id}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Parse HTML and convert to markdown
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Convert to markdown using markdownify
            url_entry.content = md(str(soup), strip=['a', 'img'])
            url_entry.status = URLStatus.COMPLETE
            url_entry.error = None

        except Exception as e:
            logger.error(f"Error scraping URL {request.url}: {e}", exc_info=True)
            url_entry.status = URLStatus.ERROR
            url_entry.error = str(e)
            url_entry.content = None

        # Update storage
        if existing_url:
            urls = [url_entry if url.id == url_entry.id else url for url in urls]
        else:
            urls.append(url_entry)
        
        self._save_urls(urls)
        return ScrapeResponse(url_entry=url_entry)

    def get_url_content(self, url_id: UUID) -> Optional[URLEntry]:
        """Get content for a specific URL"""
        return self._get_url_entry(url_id)

    def get_conversation_urls(self, conversation_id: str) -> list[URLEntry]:
        """Get all URLs for a specific conversation"""
        urls = self._load_urls()
        return [url for url in urls if url.conversation_id == conversation_id]
