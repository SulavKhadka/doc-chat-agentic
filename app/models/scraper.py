from pydantic import BaseModel, Field, HttpUrl, UUID4
from typing import Optional
from datetime import datetime
from uuid import uuid4
from enum import Enum

class ScrapingStatus(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    ERROR = "error"

class URLEntry(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    url: HttpUrl
    status: ScrapingStatus = ScrapingStatus.PENDING
    content: Optional[str] = Field(default=None, description="Markdown content converted from the scraped webpage HTML")
    error_message: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)

class ScrapeRequest(BaseModel):
    url: HttpUrl
    force_refresh: bool = False

class ScrapeResponse(BaseModel):
    url_entry: URLEntry
    job_id: UUID4
