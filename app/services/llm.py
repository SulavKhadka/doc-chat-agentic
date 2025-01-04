from typing import Optional
import httpx
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/",  # Required for OpenRouter
            "Content-Type": "application/json"
        }
    
    async def _call_llm(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Base method to call OpenRouter API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": settings.DEFAULT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens or settings.MAX_TOKENS,
                    "temperature": settings.TEMPERATURE
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def generate_topic(self, conversation_text: str) -> str:
        """Generate a concise topic/title for a conversation"""
        prompt = f"""Given the following conversation, generate a short (2-5 words) topic that captures its main theme:

{conversation_text}

Topic:"""
        return await self._call_llm(prompt, max_tokens=20)

    async def clean_scraped_content(self, content: str) -> str:
        """Clean and structure scraped content using LLM"""
        prompt = f"""Clean and structure the following scraped content. Remove any irrelevant information, 
fix formatting issues, and ensure it's well-organized:

{content}

Cleaned content:"""
        return await self._call_llm(prompt)

    async def remove_webpage_noise(self, markdown_content: str) -> str:
        """Remove unnecessary webpage elements while preserving important content.
        
        This method takes markdown-formatted webpage content and removes navigation elements,
        footers, sidebars, and other non-essential content while preserving:
        - Game statistics and scores
        - Article text and headlines
        - Player information and performance data
        - Team news and updates
        - Important tables and lists
        """
        prompt = f"""You are an AI agent tasked with cleaning up a markdown-formatted version of a webpage. Your job is to remove unnecessary content while preserving the important information. Here is the markdown content you will be working with:

<markdown_content>
{markdown_content}
</markdown_content>

Your task is to carefully remove extraneous elements that are not part of the main content, such as navigation menus, footers, and other website-specific elements that may have been left over from the scraping and markdown conversion process. It is crucial that you preserve all the main content, including game stats, articles, and other high-information content.

Specifically, you should remove:
1. Navigation menu items
2. Footer text
3. Sidebar content that is not directly related to the main content
4. Social media links and sharing buttons
5. Advertisement text
6. Copyright notices and terms of service links
7. Search bar text

However, be extremely cautious in your removal process. It is better to leave something in if you are unsure whether it's important. The preservation of actual content is of utmost importance.

When making decisions about what to remove:
- If an element seems like it could be part of the main content, leave it in.
- Do not remove headings, subheadings, or any text that appears to be part of an article or main content.
- Keep all statistics, scores, player information, and game-related data.
- Preserve any tables or lists that contain relevant information.
- Do not alter or change any of the content you keep - only remove unnecessary elements.

After processing the content, provide your output in the following format:

<cleaned_content>
[Insert the cleaned markdown content here, with unnecessary elements removed]
</cleaned_content>

<removal_summary>
[Provide a brief summary of what types of elements you removed, without going into specific details about the content]
</removal_summary>

Remember, your primary goal is to preserve the integrity of the main content while only removing clearly extraneous website elements. When in doubt, err on the side of keeping content rather than removing it."""
        return await self._call_llm(prompt)

# Create global instance
llm_service = LLMService() 