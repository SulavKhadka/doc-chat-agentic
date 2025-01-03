import streamlit as st
import requests
from datetime import datetime
import json
from typing import List, Dict, Optional
import time
from uuid import UUID
import httpx
from urllib.parse import urljoin

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Configure Streamlit page
st.set_page_config(
    page_title="NBA Chat Assistant",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for iMessage-like interface
st.markdown("""
<style>
    /* Chat container styling */
    .chat-container {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    /* User message styling */
    .user-message {
        background-color: #007AFF;
        color: white;
        margin-left: auto;
        border-radius: 20px 20px 5px 20px;
        padding: 10px 15px;
    }
    
    /* Bot message styling */
    .bot-message {
        background-color: #E9ECEF;
        color: black;
        margin-right: auto;
        border-radius: 20px 20px 20px 5px;
        padding: 10px 15px;
    }
    
    /* URL input styling */
    .url-input {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #007AFF;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'url_entries' not in st.session_state:
    st.session_state.url_entries = {}  # Dict[UUID, Dict]

async def fetch_job_status(job_id: UUID) -> dict:
    """Fetch job status from API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/v1/scraper/status/{job_id}"
        )
        response.raise_for_status()
        return response.json()

async def fetch_url_content(url_id: UUID) -> dict:
    """Fetch URL content from API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/v1/scraper/content/{url_id}"
        )
        response.raise_for_status()
        return response.json()

def submit_url(url: str) -> dict:
    """Submit URL for scraping"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/scraper/url",
            json={"url": url, "force_refresh": False}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        raise

def send_message(message: str) -> dict:
    """Send message to chat API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat/message",
            json={"message": message}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        raise

def update_context(conversation_id: UUID, context: str):
    """Update conversation context"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat/conversation/{conversation_id}/context",
            json={"context": context}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        raise

def update_url_context(url_id: UUID):
    """Update chat context with URL content"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat/context/{url_id}"
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        raise

def display_message(role: str, content: str, timestamp: datetime):
    """Display a message in iMessage style"""
    if role == "user":
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="chat-container user-message">
                {content}
                <div style="font-size: 0.7em; text-align: right; opacity: 0.7;">
                    {timestamp.strftime('%I:%M %p')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start;">
            <div class="chat-container bot-message">
                {content}
                <div style="font-size: 0.7em; text-align: right; opacity: 0.7;">
                    {timestamp.strftime('%I:%M %p')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_url_entry(entry: dict):
    """Display a single URL entry with status and actions"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.text_input(
            "URL",
            value=entry["url"],
            key=f"url_{entry['id']}",
            disabled=True
        )
    
    with col2:
        status_color = {
            "pending": "🟡",
            "loading": "🟠",
            "complete": "🟢",
            "error": "🔴"
        }.get(entry["status"], "⚪")
        st.write(f"{status_color} {entry['status'].title()}")
    
    with col3:
        if st.button("🔄", key=f"refresh_{entry['id']}", help="Refresh URL"):
            # Resubmit URL for scraping
            response = submit_url(entry["url"])
            st.session_state.url_entries[UUID(entry["id"])] = response["url_entry"]
            st.rerun()

def main():
    # Sidebar for URL management
    with st.sidebar:
        st.title("📚 URL Manager")
        st.markdown("---")
        
        # New URL input
        with st.form(key="url_form"):
            new_url = st.text_input("Add new URL", key="new_url_input")
            submit = st.form_submit_button("Add URL")
            
            if submit and new_url:
                try:
                    # Submit URL for scraping
                    response = submit_url(new_url)
                    url_entry = response["url_entry"]
                    url_id = UUID(url_entry["id"])
                    st.session_state.url_entries[url_id] = url_entry
                    
                    # Update chat context with the scraped content
                    update_url_context(url_id)
                    st.success("URL submitted and added to chat context!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error submitting URL: {str(e)}")
        
        st.markdown("---")
        
        # Display existing URLs
        if st.session_state.url_entries:
            st.subheader("📋 Current URLs")
            for entry in st.session_state.url_entries.values():
                display_url_entry(entry)
        else:
            st.info("No URLs added yet")

    # Main chat interface
    st.title("🏀 NBA Chat Assistant")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            display_message(
                role=message["role"],
                content=message["content"],
                timestamp=message["timestamp"]
            )
    
    # Chat input
    st.markdown("---")
    message = st.chat_input("Type your message here...")
    
    if message:
        # Add user message to UI
        timestamp = datetime.now()
        st.session_state.messages.append({
            "role": "user",
            "content": message,
            "timestamp": timestamp
        })
        
        try:
            # Send message to API
            response = send_message(message)
            
            # Add assistant response to UI
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["message"]["content"],
                "timestamp": datetime.now()  # Use current time since API doesn't send timestamp
            })
        except Exception as e:
            st.error(f"Error sending message: {str(e)}")
        
        # Rerun to update chat
        st.rerun()

if __name__ == "__main__":
    main()
