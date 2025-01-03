from bs4 import BeautifulSoup
from markdownify import markdownify
from typing import Dict, Optional, List
from pydantic import UUID4
import json
from datetime import datetime
from pathlib import Path
import requests
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.models.scraper import (
    URLEntry,
    ScrapeRequest,
    ScrapeResponse,
    ScrapingStatus
)

class ScraperService:
    def __init__(self):
        pass

    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to Markdown using markdownify"""
        try:
            logger.info("Converting HTML to Markdown using markdownify")
            logger.debug(f"Input HTML preview (first 200 chars): {html_content[:200]}")
            
            # Clean the HTML first using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup(['script', 'style']):
                tag.decompose()
            cleaned_html = str(soup)
            
            # Convert to markdown using markdownify
            markdown = markdownify(cleaned_html, strip=['a', 'img'])
            
            if not markdown or markdown.isspace():
                logger.error("Conversion resulted in empty markdown")
                raise ValueError("Conversion resulted in empty markdown")
                
            logger.debug(f"Output Markdown preview: {markdown}")
            return markdown
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}", exc_info=True)
            # As a fallback, try using BeautifulSoup to extract text
            try:
                logger.info("Attempting fallback text extraction with BeautifulSoup")
                soup = BeautifulSoup(html_content, 'html.parser')
                # Remove unwanted elements
                for tag in soup(['script', 'style']):
                    tag.decompose()
                # Get text with some basic formatting
                text = soup.get_text(separator='\n\n')
                return text
            except Exception as fallback_error:
                logger.error(f"Fallback extraction failed: {str(fallback_error)}")
                return "Error: Could not convert content to readable format"
    
    def _save_content(self, entry: URLEntry) -> None:
        """Save scraped content and URL to file"""
        file_path = settings.SCRAPED_CONTENT_DIR / f"{entry.id}.json"
        data = {
            "document": {
                "source": str(entry.url),
                "document_content": entry.content if entry.content else "",
                "last_updated": entry.last_updated.isoformat()
            }
        }
        with open(file_path, "w") as f:
            json.dump(data, f)
    
    def _load_content(self, entry_id: UUID4) -> Optional[dict]:
        """Load scraped content and URL from file"""
        file_path = settings.SCRAPED_CONTENT_DIR / f"{entry_id}.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
                return data["document"]
        return None
    
    def _should_use_scraper_api(self, url: str) -> bool:
        """Determine if we should use ScraperAPI for this URL"""
        protected_domains = [
            "rotogrinders.com",
            "nba.com"
            # Add other domains that need ScraperAPI here
        ]
        return any(domain in url.lower() for domain in protected_domains)
    
    def _scrape_with_scraper_api(self, url: str) -> str:
        """Scrape a URL using ScraperAPI"""
        payload = {
            'api_key': settings.SCRAPER_API_KEY,
            'url': url,
            'render': True
        }
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=settings.SCRAPER_TIMEOUT)
        text = response.text
        return self._html_to_markdown(text)
    
    def _scrape_single_url(self, url: str) -> str:
        """Scrape a single URL and return markdown content"""
        logger.info(f"Scraping URL: {url}")
        if self._should_use_scraper_api(url):
            content = self._scrape_with_scraper_api(url)
        else:
            response = requests.get(url, timeout=settings.SCRAPER_TIMEOUT)
            html = response.text
            # Convert directly to markdown without intermediate soup step
            content = self._html_to_markdown(html)
        
        if len(content) > settings.MAX_CONTENT_LENGTH:
            logger.warning(f"Content exceeds max length ({len(content)} > {settings.MAX_CONTENT_LENGTH})")
            content = content[:settings.MAX_CONTENT_LENGTH] + "..."
        
        return content
    
    def scrape_url(self, request: ScrapeRequest) -> ScrapeResponse:
        """Process a single URL scraping request synchronously"""
        entry = URLEntry(url=request.url)
        
        try:
            # Perform scraping
            content = self._scrape_single_url(str(request.url))
            
            # Update entry
            entry.content = content
            entry.status = ScrapingStatus.COMPLETE
            entry.last_updated = datetime.now()
            
            # Save to file
            self._save_content(entry)
            
            return ScrapeResponse(
                url_entry=entry,
                job_id=entry.id
            )
        except Exception as e:
            entry.status = ScrapingStatus.ERROR
            entry.error_message = str(e)
            raise
    
    def get_url_entry(self, url_id: UUID4) -> Optional[URLEntry]:
        """Get URL entry with content from file"""
        data = self._load_content(url_id)
        if data:
            return URLEntry(
                id=url_id,
                url=data["source"],
                status=ScrapingStatus.COMPLETE,
                content=data["document_content"],
                last_updated=datetime.fromisoformat(data["last_updated"])
            )
        return None
    
    def cleanup(self):
        """Cleanup resources - no longer needed with requests"""
        pass
