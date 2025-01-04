from enum import Enum
from pydantic import BaseModel, UUID4
from typing import Optional
from uuid import UUID

class URLStatus(str, Enum):
    PENDING = "pending"
    LOADING = "loading"
    COMPLETE = "complete"
    ERROR = "error"

class URLEntry(BaseModel):
    id: UUID
    url: str
    status: URLStatus
    conversation_id: str
    raw_content: Optional[str] = None  # Initial markdown content
    content: Optional[str] = None      # LLM-cleaned content
    error: Optional[str] = None

class ScrapeRequest(BaseModel):
    url: str
    conversation_id: str
    force_refresh: bool = False

class ScrapeResponse(BaseModel):
    url_entry: URLEntry
