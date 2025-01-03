from transformers import AutoTokenizer
import openai
from typing import List, Dict, Optional
import logging
from app.core.config import settings
from app.models.scraper import URLEntry
import re

logger = logging.getLogger(__name__)

# Create client
OAI_CLIENT = openai.OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key = settings.OPENROUTER_API_KEY,
)

def get_llm_response(messages: List[Dict[str, str]], model_name: str):
    logger.debug(f"Sending request to LLM with {len(messages)} messages")
    logger.debug("Messages being sent to LLM:")
    for i, msg in enumerate(messages):
        logger.debug(f"Message {i}: {msg['role']} - {msg['content'][:200]}...")
    
    chat_completion = OAI_CLIENT.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=1536,
        temperature=0.4
    )
    logger.debug(f"Received response from LLM: {len(chat_completion.choices[0].message.content)} chars")
    return chat_completion

class ChatService:
    def __init__(self, model: str, tok_model: str, system: str = ""):
        logger.info(f"Initializing ChatService with model={model}, tokenizer={tok_model}")
        logger.info("=== FULL SYSTEM MESSAGE AT INIT START ===")
        logger.info(system)
        logger.info("=== END FULL SYSTEM MESSAGE ===")
        
        # Ensure system message has proper documents section
        if "<documents>" not in system or "</documents>" not in system:
            logger.warning("System message missing documents tags, adding them")
            # Find the end of the main system prompt
            if system:
                system = system.rstrip() + "\n\n<documents>\n</documents>"
            else:
                system = "<documents>\n</documents>"
        
        self.system = system
        self.model = model
        self.tokenizer = AutoTokenizer.from_pretrained(tok_model)
        self.max_message_tokens = 65536

        self.purged_messages = []
        self.purged_messages_token_count = []
        self.messages = []
        self.messages_token_counts = []
        self.total_messages_tokens = 0
        
        # Store scraped content separately
        self.scraped_content = {}

        if self.system:
            logger.info("Adding system prompt to messages")
            self.messages.append({"role": "system", "content": system})
            self.messages_token_counts.append(len(self.tokenizer.encode(system)))
            self.total_messages_tokens = len(self.tokenizer.encode(system))
            logger.debug(f"System prompt tokens: {self.messages_token_counts[-1]}")
            self.verify_system_content("AFTER_INIT")
    
    def _update_system_message(self) -> None:
        """Update system message with current scraped content"""
        logger.info("=== UPDATING SYSTEM MESSAGE START ===")
        logger.info(f"Current number of scraped documents: {len(self.scraped_content)}")
        
        # Split system message into parts using regex to preserve all content
        pattern = r'(<documents>.*?</documents>)'
        parts = re.split(pattern, self.system, flags=re.DOTALL)
        
        if len(parts) != 3:  # Should be: [before, documents section, after]
            logger.error(f"Invalid system message structure. Got {len(parts)} parts, expected 3")
            logger.error(f"System message preview: {self.system[:200]}...")
            return
            
        before_docs, _, after_docs = parts
        
        # Combine all scraped content in XML format
        documents_content = ""
        for idx, (url, content) in enumerate(self.scraped_content.items(), 1):
            logger.debug(f"Processing document {idx} from URL: {url}")
            if documents_content:
                documents_content += "\n"
            documents_content += f'  <document index="{idx}">\n'
            documents_content += f'    <source>{url}</source>\n'
            documents_content += f'    <document_content>\n      {content}\n    </document_content>\n'
            documents_content += '  </document>'
        
        # Create new system message preserving content before and after documents
        new_system = f"{before_docs}<documents>\n{documents_content}\n</documents>{after_docs}"
        
        # Update system property
        self.system = new_system
        
        # Update in messages list
        if self.messages and self.messages[0]["role"] == "system":
            prev_tokens = self.messages_token_counts[0]
            self.messages[0]["content"] = new_system
            # Recalculate token count
            new_tokens = len(self.tokenizer.encode(new_system))
            self.messages_token_counts[0] = new_tokens
            self.total_messages_tokens = sum(self.messages_token_counts)
            logger.info(f"Token count changed from {prev_tokens} to {new_tokens}")
        
        logger.info("=== UPDATING SYSTEM MESSAGE END ===")
        logger.info(f"Updated system message preview: {new_system[:200]}...")
    
    def update_context(self, url: str, content: str) -> None:
        """Add or update content in the conversation context"""
        if not content:
            logger.warning(f"No content to add for URL: {url}")
            return
            
        logger.info(f"Adding/updating content from URL: {url}")
        
        # Store content
        self.scraped_content[url] = content
        
        # Update system message
        self._update_system_message()
        
        logger.info("=== FINAL CONTEXT UPDATE VERIFICATION ===")
        logger.info(f"Current scraped content URLs: {list(self.scraped_content.keys())}")
        logger.info(f"System message preview: {self.system[:200]}...")
        if self.messages:
            logger.info(f"First message preview: {self.messages[0]['content'][:200]}...")
        logger.info("=== END CONTEXT UPDATE VERIFICATION ===")
    
    def remove_url_content(self, url: str) -> None:
        """Remove content from a specific URL in the scraped pages data section"""
        if not url:
            return

        logger.info(f"Removing content for URL: {url}")
        
        # Remove content
        if url in self.scraped_content:
            del self.scraped_content[url]
            
            # Update system message
            self._update_system_message()
            
            logger.info("=== FINAL REMOVE URL VERIFICATION ===")
            logger.info(f"Current scraped content URLs: {list(self.scraped_content.keys())}")
            logger.info(f"System message preview: {self.system[:200]}...")
            if self.messages:
                logger.info(f"First message preview: {self.messages[0]['content'][:200]}...")
            logger.info("=== END FINAL REMOVE URL VERIFICATION ===")
        else:
            logger.warning(f"URL {url} not found in scraped content")
    
    def process_message(self, message: str) -> str:
        logger.info("Processing new message")
        logger.info("=== PROCESS MESSAGE START STATE ===")
        logger.info(f"System message preview: {self.system[:200]}...")
        if self.messages:
            logger.info(f"First message preview: {self.messages[0]['content'][:200]}...")
        logger.info("=== END PROCESS MESSAGE START STATE ===")
        
        # Ensure system message is intact
        pattern = r'(<documents>.*?</documents>)'
        if not re.search(pattern, self.system, re.DOTALL):
            logger.error("System message corrupted, attempting to restore from messages list")
            if self.messages and self.messages[0]["role"] == "system":
                self.system = self.messages[0]["content"]
            else:
                logger.error("Could not restore system message!")
                return "Error: System message corrupted"
        
        # Add user message
        logger.info("Adding user message")
        self.messages.append({"role": "user", "content": message})
        message_tokens = len(self.tokenizer.encode(message))
        self.messages_token_counts.append(message_tokens)
        self.total_messages_tokens += message_tokens
        logger.debug(f"Added user message with {message_tokens} tokens")
        
        # Get response from LLM
        logger.info("Getting response from LLM")
        completion = get_llm_response(messages=self.messages, model_name=self.model)
        response = completion.choices[0].message.content
        
        # Add assistant response
        logger.info("Adding assistant response")
        self.messages.append({"role": "assistant", "content": response})
        response_tokens = len(self.tokenizer.encode(response))
        self.messages_token_counts.append(response_tokens)
        self.total_messages_tokens += response_tokens
        logger.debug(f"Added assistant response with {response_tokens} tokens")
        
        return response
    
    def execute(self):
        logger.info("=== EXECUTE DEBUG ===")
        if self.messages and self.messages[0]["role"] == "system":
            pattern = r'\[SCRAPED_PAGES_DATA\](.*?)\[/SCRAPED_PAGES_DATA\]'
            match = re.search(pattern, self.messages[0]["content"], re.DOTALL)
            if match:
                logger.info(f"Found scraped pages content before LLM call: '{match.group(1)}'")
            else:
                logger.error("No scraped pages content found before LLM call!")
        logger.info("=== END EXECUTE DEBUG ===")
        
        logger.debug(f"Executing LLM call with {len(self.messages)} messages")
        completion = get_llm_response(messages=self.messages, model_name=self.model)
        return completion

    def rolling_memory(self):
        logger.info("=== ROLLING MEMORY DEBUG ===")
        # Check content before memory management
        if self.messages and self.messages[0]["role"] == "system":
            pattern = r'\[SCRAPED_PAGES_DATA\](.*?)\[/SCRAPED_PAGES_DATA\]'
            match = re.search(pattern, self.messages[0]["content"], re.DOTALL)
            if match:
                logger.info(f"Found scraped pages content before memory cleanup: '{match.group(1)}'")
            else:
                logger.error("No scraped pages content found before memory cleanup!")
        
        if self.total_messages_tokens >= self.max_message_tokens:
            logger.info("Starting memory management")
            logger.debug(f"Current total tokens: {self.total_messages_tokens}")
            logger.debug(f"Max tokens allowed: {self.max_message_tokens}")
        
        while self.total_messages_tokens >= self.max_message_tokens:
            # Don't remove system message or initial context
            if len(self.messages) <= 2:
                logger.warning("Cannot remove more messages - reached system/context messages")
                break
                
            # Remove oldest non-system messages
            removed_message = self.messages.pop(2)  # Start from index 2 to preserve system and context
            removed_tokens = self.messages_token_counts.pop(2)
            
            self.purged_messages.append(removed_message)
            self.purged_messages_token_count.append(removed_tokens)
            self.total_messages_tokens -= removed_tokens
            
            logger.debug(f"Removed message: {removed_message.get('role')} ({removed_tokens} tokens)")
            logger.debug(f"New total tokens: {self.total_messages_tokens}")
        
        # Check content after memory management
        if self.messages and self.messages[0]["role"] == "system":
            match = re.search(pattern, self.messages[0]["content"], re.DOTALL)
            if match:
                logger.info(f"Found scraped pages content after memory cleanup: '{match.group(1)}'")
            else:
                logger.error("No scraped pages content found after memory cleanup!")
        
        if self.total_messages_tokens >= self.max_message_tokens:
            logger.warning("Memory management complete but still at token limit")
        
        logger.info("=== END ROLLING MEMORY DEBUG ===")

    def verify_system_content(self, location: str) -> None:
        """Helper method to verify system message content"""
        logger.info(f"=== VERIFY SYSTEM CONTENT AT {location} ===")
        logger.info(f"System message length: {len(self.system)}")
        logger.info(f"Number of stored documents: {len(self.scraped_content)}")
        
        if self.messages and self.messages[0]["role"] == "system":
            # Check self.system
            pattern = r'<documents>(.*?)</documents>'
            sys_match = re.search(pattern, self.system, re.DOTALL)
            if sys_match:
                docs_content = sys_match.group(1)
                logger.info(f"Documents section length in self.system: {len(docs_content)}")
                logger.debug(f"Documents content preview: {docs_content[:200]}...")
            else:
                logger.error("No documents section found in self.system!")
                logger.error(f"System message preview: {self.system[:200]}...")
            
            # Check messages list
            msg_match = re.search(pattern, self.messages[0]["content"], re.DOTALL)
            if msg_match:
                docs_content = msg_match.group(1)
                logger.info(f"Documents section length in messages[0]: {len(docs_content)}")
                logger.debug(f"Messages[0] documents preview: {docs_content[:200]}...")
            else:
                logger.error("No documents section found in messages[0]!")
            
            # Check if they match
            if self.system != self.messages[0]["content"]:
                logger.error("Mismatch between self.system and messages[0]!")
                logger.error("System length vs message length: " +
                           f"{len(self.system)} vs {len(self.messages[0]['content'])}")
        
        logger.info(f"=== END VERIFY AT {location} ===")

    def get_scraped_content(self) -> str:
        """Helper method to get current scraped content"""
        pattern = r'<documents>(.*?)</documents>'
        match = re.search(pattern, self.system, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def clear_context(self) -> None:
        """Clear all scraped content from the chat context"""
        logger.info("Clearing chat context")
        
        # Clear scraped content
        self.scraped_content = {}
        
        # Update system message
        self._update_system_message()
        
        logger.info("=== CLEAR CONTEXT VERIFICATION ===")
        logger.info(f"Scraped content count: {len(self.scraped_content)}")
        logger.info(f"System message preview: {self.system[:200]}...")
        if self.messages:
            logger.info(f"First message preview: {self.messages[0]['content'][:200]}...")
        logger.info("=== END CLEAR CONTEXT VERIFICATION ===")
