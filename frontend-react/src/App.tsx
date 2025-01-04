import React, { useState, useEffect, useRef } from 'react';
import ConversationDrawer from './components/ConversationDrawer';
import URLManager from './components/URLManager';
import MarkdownMessage from './components/MarkdownMessage';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface URLEntry {
  id: string;
  url: string;
  status: 'pending' | 'loading' | 'complete' | 'error';
  conversation_id: string;
  content?: string;
  error?: string;
}

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  messages: Message[];
  urls: URLEntry[];
}

const App: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations from localStorage on mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      setConversations(JSON.parse(savedConversations));
    }
  }, []);

  // Save conversations to localStorage when updated
  useEffect(() => {
    localStorage.setItem('conversations', JSON.stringify(conversations));
  }, [conversations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateTopicForConversation = async (messages: Message[]) => {
    try {
      const response = await fetch('/api/v1/chat/generate-topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.topic;
    } catch (error) {
      console.error('Failed to generate topic:', error);
      return null;
    }
  };

  const handleNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: `New Conversation`,
      lastMessage: '',
      timestamp: new Date().toISOString(),
      messages: [],
      urls: []
    };
    setConversations([...conversations, newConversation]);
    setSelectedConversationId(newConversation.id);
    setMessages([]);
  };

  const handleSelectConversation = (id: string) => {
    const conversation = conversations.find(c => c.id === id);
    if (conversation) {
      setSelectedConversationId(id);
      setMessages(conversation.messages);
    }
  };

  const updateChatContext = async (conversationId: string, urls: URLEntry[]) => {
    try {
      // First, clear the existing context
      await fetch('/api/v1/chat/context/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: conversationId }),
      });

      // Then add all URLs to the context in sequence
      for (const url of urls) {
        if (url.status === 'complete' && url.content) {
          await fetch(`/api/v1/chat/context/${url.id}`, {
            method: 'POST',
          });
        }
      }
    } catch (error) {
      console.error('Failed to update chat context:', error);
      setError('Failed to update chat context with URLs');
    }
  };

  const handleAddUrl = async (url: string) => {
    if (!selectedConversationId) return;

    try {
      const response = await fetch('/api/v1/scraper/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          url,
          conversation_id: selectedConversationId,
          force_refresh: false 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update conversations with the new URL
      setConversations(prevConversations =>
        prevConversations.map(conv =>
          conv.id === selectedConversationId
            ? {
                ...conv,
                urls: [...conv.urls, { ...data.url_entry, conversation_id: selectedConversationId }],
              }
            : conv
        )
      );

      // Get the updated conversation
      const updatedConversation = conversations.find(c => c.id === selectedConversationId);
      if (updatedConversation) {
        // Update chat context with all URLs
        await updateChatContext(selectedConversationId, [
          ...updatedConversation.urls,
          { ...data.url_entry, conversation_id: selectedConversationId }
        ]);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to add URL');
      throw error;
    }
  };

  const handleRefreshUrl = async (entry: URLEntry) => {
    try {
      const response = await fetch('/api/v1/scraper/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          url: entry.url,
          conversation_id: entry.conversation_id,
          force_refresh: true 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update conversations with the refreshed URL
      setConversations(prevConversations =>
        prevConversations.map(conv =>
          conv.id === entry.conversation_id
            ? {
                ...conv,
                urls: conv.urls.map(url =>
                  url.id === entry.id ? { ...data.url_entry, conversation_id: entry.conversation_id } : url
                ),
              }
            : conv
        )
      );

      // Get the updated conversation
      const updatedConversation = conversations.find(c => c.id === entry.conversation_id);
      if (updatedConversation) {
        // Update chat context with all URLs
        await updateChatContext(entry.conversation_id, updatedConversation.urls);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to refresh URL');
      throw error;
    }
  };

  const handleEditUrl = async (entry: URLEntry, newUrl: string) => {
    try {
      // Add the new URL
      const response = await fetch('/api/v1/scraper/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          url: newUrl,
          conversation_id: entry.conversation_id,
          force_refresh: true 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update conversations with the edited URL
      setConversations(prevConversations =>
        prevConversations.map(conv =>
          conv.id === entry.conversation_id
            ? {
                ...conv,
                urls: conv.urls.map(url =>
                  url.id === entry.id ? { ...data.url_entry, conversation_id: entry.conversation_id } : url
                ),
              }
            : conv
        )
      );

      // Get the updated conversation
      const updatedConversation = conversations.find(c => c.id === entry.conversation_id);
      if (updatedConversation) {
        // Update chat context with all URLs
        await updateChatContext(entry.conversation_id, updatedConversation.urls);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to edit URL');
      throw error;
    }
  };

  const handleDeleteUrl = async (entry: URLEntry) => {
    try {
      // Update conversations state first
      setConversations(prevConversations =>
        prevConversations.map(conv =>
          conv.id === entry.conversation_id
            ? {
                ...conv,
                urls: conv.urls.filter(url => url.id !== entry.id),
              }
            : conv
        )
      );

      // Get the updated conversation
      const updatedConversation = conversations.find(c => c.id === entry.conversation_id);
      if (updatedConversation) {
        // Update chat context with remaining URLs
        await updateChatContext(
          entry.conversation_id, 
          updatedConversation.urls.filter(url => url.id !== entry.id)
        );
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to delete URL');
      throw error;
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || !selectedConversationId) return;

    const newMessage: Message = {
      role: 'user',
      content: userInput,
      timestamp: new Date().toISOString(),
    };

    // Update messages state
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);

    // Update conversations state
    setConversations(prevConversations => 
      prevConversations.map(conv => 
        conv.id === selectedConversationId
          ? {
              ...conv,
              messages: updatedMessages,
              lastMessage: userInput,
              timestamp: new Date().toISOString(),
            }
          : conv
      )
    );

    setUserInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userInput,
          conversation_id: selectedConversationId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message?.content || 'No response content',
        timestamp: new Date().toISOString(),
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      
      // Generate new topic after assistant response if this is the first exchange
      let newTitle = null;
      if (finalMessages.length <= 2) {
        newTitle = await generateTopicForConversation(finalMessages);
      }
      
      setMessages(finalMessages);
      setConversations(prevConversations =>
        prevConversations.map(conv =>
          conv.id === selectedConversationId
            ? {
                ...conv,
                messages: finalMessages,
                lastMessage: assistantMessage.content,
                timestamp: assistantMessage.timestamp,
                ...(newTitle && { title: newTitle }),
              }
            : conv
        )
      );
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const selectedConversation = conversations.find(c => c.id === selectedConversationId);

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Conversation Drawer */}
      <ConversationDrawer
        conversations={conversations}
        selectedId={selectedConversationId}
        onSelectConversation={handleSelectConversation}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-100">
            {selectedConversationId 
              ? conversations.find(c => c.id === selectedConversationId)?.title 
              : 'Select a conversation'}
          </h1>
          <button
            onClick={handleNewConversation}
            className="px-4 py-2 bg-indigo-600 text-gray-100 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            New Conversation
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-900">
          {messages.map((message, index) => (
            <MarkdownMessage
              key={index}
              content={message.content}
              isAssistant={message.role === 'assistant'}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* URL Manager */}
        {selectedConversationId && (
          <URLManager
            conversationId={selectedConversationId}
            urls={selectedConversation?.urls || []}
            onAddUrl={handleAddUrl}
            onRefreshUrl={handleRefreshUrl}
            onDeleteUrl={handleDeleteUrl}
            onEditUrl={handleEditUrl}
          />
        )}

        {/* Error Message */}
        {error && (
          <div className="px-4 py-2 bg-red-900/50 text-red-200 text-sm border border-red-700">
            {error}
          </div>
        )}

        {/* Input Area */}
        <div className="bg-gray-800 border-t border-gray-700 p-4">
          <form onSubmit={handleSendMessage} className="flex gap-4">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg 
                       text-gray-100 placeholder-gray-400
                       focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-indigo-600 text-gray-100 rounded-lg 
                       hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default App;
