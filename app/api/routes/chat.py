from fastapi import APIRouter, HTTPException, Depends, Body
from uuid import UUID
import logging
from app.services.chat import ChatService
from app.services.scraper import ScraperService
from app.api.dependencies import get_chat_service, get_scraper_service
from app.models.chat import ChatRequest, ChatResponse
from app.models.scraper import URLEntry
import asyncio
from functools import partial

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/message")
async def send_message(
    request: dict = Body(...),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Send a message to the chat bot and get a response.
    """
    try:
        message = request.get('message')
        logger.info(f"Received chat message request")
        logger.debug(f"Message content: {message}")
        
        # Run the synchronous process_message in a thread pool
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            partial(chat_service.process_message, message)
        )
        logger.info("Successfully processed message")
        logger.debug(f"Response content: {response}")
        
        return {
            "message": {
                "role": "assistant",
                "content": response,
                "timestamp": None
            }
        }
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context/{url_id}")
async def update_context(
    url_id: UUID,
    chat_service: ChatService = Depends(get_chat_service),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """
    Update the chat context with content from a scraped URL.
    """
    try:
        logger.info(f"Updating context from URL ID: {url_id}")
        
        # Get the URL entry with its content
        loop = asyncio.get_running_loop()
        url_entry = await loop.run_in_executor(
            None,
            partial(scraper_service.get_url_entry, url_id)
        )
        if not url_entry:
            logger.warning(f"URL content not found for ID: {url_id}")
            raise HTTPException(status_code=404, detail="URL content not found")
        
        logger.debug(f"Retrieved content for URL: {url_entry.url}")
        content_preview = url_entry.content[:100] + "..." if url_entry.content and len(url_entry.content) > 100 else "No content"
        logger.debug(f"Content preview: {content_preview}")
        
        # Add the content to chat context
        await loop.run_in_executor(
            None,
            partial(chat_service.add_url_content, url_entry)
        )
        logger.info("Successfully updated context from URL")
        
        return {"status": "success", "message": "Context updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating context from URL: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/context/{url}")
async def remove_url_from_context(
    url: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Remove content from a specific URL from the chat context.
    """
    try:
        logger.info(f"Removing content for URL: {url}")
        # Run the synchronous remove_url_content in a thread pool
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(chat_service.remove_url_content, url)
        )
        logger.info("Successfully removed URL content from context")
        
        return {"status": "success", "message": "URL content removed successfully"}
    except Exception as e:
        logger.error(f"Error removing URL content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
