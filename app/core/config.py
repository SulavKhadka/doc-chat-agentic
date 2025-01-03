from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path
from secret_keys import OPENROUTER_API_KEY, SCRAPER_API_KEY

class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NBA Chat Assistant"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:8000"]
    
    # OpenRouter
    OPENROUTER_API_KEY: str = OPENROUTER_API_KEY
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # ScraperAPI
    SCRAPER_API_KEY: str = SCRAPER_API_KEY
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    SCRAPED_CONTENT_DIR: Path = STORAGE_DIR / "scraped_content"
    
    # Model settings
    DEFAULT_MODEL: str = "deepseek/deepseek-chat"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.2
    
    # Scraping settings
    SCRAPER_TIMEOUT: int = 60  # seconds
    MAX_CONTENT_LENGTH: int = 100_000_000  # characters
    
    class Config:
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.SCRAPED_CONTENT_DIR, exist_ok=True)
