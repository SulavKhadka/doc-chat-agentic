# NBA Chat Assistant

A sophisticated chat application that combines web scraping capabilities with Large Language Models to provide context-aware conversations about NBA-related topics. The application can scrape web content, maintain conversation context, and provide intelligent responses using the latest LLM technology.

## Features

- **Web Scraping Integration**: Utilizes ScraperAPI for reliable web content extraction
- **Context-Aware Conversations**: Maintains conversation history and scraped content context
- **LLM Integration**: Uses OpenRouter API for accessing advanced language models
- **Memory Management**: Implements rolling memory to handle token limits efficiently
- **Real-time Content Updates**: Dynamic system context updates with new scraped content
- **FastAPI Backend**: High-performance asynchronous API server
- **React Frontend**: Modern, responsive user interface

## Architecture

### Backend Components

#### Core (`app/core/`)
- `config.py`: Application configuration including API keys, model settings, and paths
- `database.py`: Database connection and management

#### API Routes (`app/api/routes/`)
- `chat.py`: Endpoints for chat functionality
- `scraper.py`: Endpoints for web scraping operations

#### Services (`app/services/`)
- `chat.py`: Chat service with context management and LLM integration
- `scraper.py`: Web scraping service with content processing
- `llm.py`: LLM service integration

#### Models (`app/models/`)
- `chat.py`: Chat-related data models
- `scraper.py`: Scraping-related data models

### Frontend Components

- React-based user interface
- Real-time chat interface
- URL submission and content display
- Context management controls

## Technical Details

### Chat Service Features

1. **Context Management**
   - Maintains conversation history
   - Manages scraped content in XML format
   - Updates system context dynamically
   - Implements rolling memory for token limit management

2. **LLM Integration**
   - Uses OpenRouter API
   - Configurable model selection
   - Token counting and management
   - Error handling and retry logic

3. **Content Processing**
   - HTML to Markdown conversion
   - Content cleaning and formatting
   - XML-based document storage
   - Source tracking for scraped content

### Scraper Service Features

1. **Web Scraping**
   - ScraperAPI integration for reliable scraping
   - HTML parsing and cleaning
   - Content storage management
   - Error handling and retry logic

2. **Content Storage**
   - JSON-based URL storage
   - File-based content storage
   - Conversation-specific content management
   - Duplicate URL handling

## Configuration

The application requires several environment variables to be set:

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# ScraperAPI Configuration
SCRAPER_API_KEY=your_scraper_api_key

# Model Settings
DEFAULT_MODEL=deepseek/deepseek-chat
MAX_TOKENS=32768
TEMPERATURE=0.2

# Server Settings
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:8000"]
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doc-chat-agentic
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend-react
npm install
```

## Running the Application

1. Start the backend server:
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend development server:
```bash
cd frontend-react
npm run dev
```

The application will be available at:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Chat Endpoints

- `POST /api/v1/chat/message`: Send a message to the chat
- `GET /api/v1/chat/context`: Get current chat context
- `DELETE /api/v1/chat/context`: Clear chat context

### Scraper Endpoints

- `POST /api/v1/scraper/url`: Scrape a new URL
- `GET /api/v1/scraper/url/{url_id}`: Get content for a specific URL
- `GET /api/v1/scraper/conversation/{conversation_id}`: Get all URLs for a conversation

## Error Handling

The application implements comprehensive error handling:

- Web scraping failures
- LLM API errors
- Token limit management
- Content processing errors
- Storage/retrieval errors

## Logging

Detailed logging is implemented throughout the application:

- Debug-level logging for development
- Info-level logging for production
- Error tracking and reporting
- Performance monitoring

## Security Considerations

- API key management
- CORS configuration
- Input validation
- Rate limiting
- Error message sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add License Information]

## Support

[Add Support Information]