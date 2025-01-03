from pydantic import BaseModel, UUID4
from typing import Optional
from enum import Enum

class URLStatus(str, Enum):
    PENDING = "pending"
    LOADING = "loading"
    COMPLETE = "complete"
    ERROR = "error"

class ScrapeRequest(BaseModel):
    url: str
    force_refresh: bool = False
    conversation_id: str

class URLEntry(BaseModel):
    id: UUID4
    url: str
    status: URLStatus
    conversation_id: str
    content: Optional[str] = None
    error: Optional[str] = None

class ScrapeResponse(BaseModel):
    url_entry: URLEntry
