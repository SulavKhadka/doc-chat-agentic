from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.scraper import scraper_router
from app.api.routes.chat import router as chat_router
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', mode='a', encoding='utf-8')
    ]
)

# Set log levels for specific modules
logging.getLogger('app.services.chat').setLevel(logging.DEBUG)
logging.getLogger('app.services.scraper').setLevel(logging.DEBUG)
logging.getLogger('app.api.routes').setLevel(logging.DEBUG)
logging.getLogger('uvicorn').setLevel(logging.INFO)
logging.getLogger('fastapi').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=True  # Enable debug mode
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
app.include_router(
    scraper_router,
    prefix=f"{settings.API_V1_STR}/scraper",
    tags=["scraper"]
)

app.include_router(
    chat_router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["chat"]
)

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {
        "message": "Welcome to NBA Chat Assistant API",
        "version": "1.0.0",
        "status": "healthy",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
