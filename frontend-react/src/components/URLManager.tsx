import React, { useState, useEffect } from 'react';
import MarkdownMessage from './MarkdownMessage';

interface URLEntry {
  id: string;
  url: string;
  status: 'pending' | 'loading' | 'complete' | 'error';
  conversation_id: string;
  content?: string;
  raw_content?: string;
  error?: string;
}

interface URLManagerProps {
  conversationId: string;
  urls: URLEntry[];
  onAddUrl: (url: string) => Promise<void>;
  onRefreshUrl: (entry: URLEntry) => Promise<void>;
  onDeleteUrl: (entry: URLEntry) => Promise<void>;
  onEditUrl: (entry: URLEntry, newUrl: string) => Promise<void>;
}

const URLManager: React.FC<URLManagerProps> = ({
  conversationId,
  urls,
  onAddUrl,
  onRefreshUrl,
  onDeleteUrl,
  onEditUrl,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [previewingId, setPreviewingId] = useState<string | null>(null);
  const [showRawContent, setShowRawContent] = useState<Record<string, boolean>>({});

  // Reset states when URL manager is collapsed
  useEffect(() => {
    if (!isExpanded) {
      setPreviewingId(null);
      setShowRawContent({});
    }
  }, [isExpanded]);

  // Reset showRawContent for an entry when its preview is closed
  useEffect(() => {
    if (!previewingId) {
      setShowRawContent({});
    }
  }, [previewingId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUrl.trim() || isLoading) return;

    setIsLoading(true);
    try {
      await onAddUrl(newUrl);
      setNewUrl('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartEdit = (entry: URLEntry) => {
    setEditingId(entry.id);
    setEditValue(entry.url);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditValue('');
  };

  const handleSaveEdit = async (entry: URLEntry) => {
    if (!editValue.trim() || editValue === entry.url) {
      handleCancelEdit();
      return;
    }

    try {
      await onEditUrl(entry, editValue);
      handleCancelEdit();
    } catch (error) {
      console.error('Failed to edit URL:', error);
    }
  };

  const handleDelete = async (entry: URLEntry) => {
    if (!window.confirm('Are you sure you want to delete this URL?')) return;
    
    try {
      await onDeleteUrl(entry);
    } catch (error) {
      console.error('Failed to delete URL:', error);
    }
  };

  const togglePreview = (entry: URLEntry) => {
    if (previewingId === entry.id) {
      setPreviewingId(null);
    } else {
      setPreviewingId(entry.id);
      setIsExpanded(true); // Ensure URL manager is expanded when preview is shown
    }
  };

  const toggleContentVersion = (entryId: string) => {
    setShowRawContent(prev => ({
      ...prev,
      [entryId]: !prev[entryId]
    }));
  };

  return (
    <div className="flex flex-col border-t border-gray-700">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2 flex items-center justify-between 
                 bg-gray-800 hover:bg-gray-700 transition-colors"
      >
        <span className="font-medium text-gray-100">
          URLs ({urls.length})
        </span>
        <svg
          className={`w-5 h-5 text-gray-400 transform transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isExpanded && (
        <div className="flex flex-col min-h-0 bg-gray-800 border-t border-gray-700">
          <form onSubmit={handleSubmit} className="p-4 border-b border-gray-700 shrink-0">
            <div className="flex gap-2">
              <input
                type="text"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="Enter URL..."
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg 
                         text-gray-100 placeholder-gray-400
                         focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 bg-indigo-600 text-gray-100 rounded-lg 
                         hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed
                         transition-colors"
              >
                {isLoading ? 'Adding...' : 'Add'}
              </button>
            </div>
          </form>

          <div className="flex-1 min-h-0 p-4 overflow-hidden">
            <div className={`space-y-2 overflow-y-auto ${previewingId ? 'h-[calc(100vh-25rem)]' : 'max-h-60'}`}>
              {urls.map((entry) => (
                <div
                  key={entry.id}
                  className={`p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow ${
                    previewingId === entry.id ? 'flex flex-col' : ''
                  }`}
                >
                  <div className={`${previewingId === entry.id ? 'flex-shrink-0' : ''}`}>
                    {editingId === entry.id ? (
                      <div className="flex gap-2 mb-2">
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded 
                                   text-gray-100 text-sm
                                   focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                        <button
                          onClick={() => handleSaveEdit(entry)}
                          className="px-2 py-1 bg-green-600 text-gray-100 rounded hover:bg-green-700 
                                   text-sm transition-colors"
                        >
                          Save
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="px-2 py-1 bg-gray-600 text-gray-100 rounded hover:bg-gray-500 
                                   text-sm transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-100 truncate">{entry.url}</div>
                    )}
                    <div className="mt-2 flex justify-between items-center">
                      <span
                        className={`
                          px-2 py-1 text-xs rounded-full
                          ${
                            entry.status === 'complete'
                              ? 'bg-green-900/50 text-green-200'
                              : entry.status === 'error'
                              ? 'bg-red-900/50 text-red-200'
                              : entry.status === 'loading'
                              ? 'bg-yellow-900/50 text-yellow-200'
                              : 'bg-gray-900/50 text-gray-200'
                          }
                        `}
                      >
                        {entry.status}
                      </span>
                      <div className="flex gap-1">
                        {entry.status === 'complete' && (
                          <button
                            onClick={() => togglePreview(entry)}
                            className={`p-1 hover:bg-gray-600 rounded-full transition-colors
                                      ${previewingId === entry.id ? 'bg-gray-600' : ''}`}
                            title={previewingId === entry.id ? "Hide content preview" : "Show content preview"}
                          >
                            👁️
                          </button>
                        )}
                        <button
                          onClick={() => handleStartEdit(entry)}
                          className="p-1 hover:bg-gray-600 rounded-full transition-colors"
                          title="Edit URL"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => onRefreshUrl(entry)}
                          className="p-1 hover:bg-gray-600 rounded-full transition-colors"
                          title="Reprocess URL"
                        >
                          🔄
                        </button>
                        <button
                          onClick={() => handleDelete(entry)}
                          className="p-1 hover:bg-gray-600 rounded-full transition-colors text-red-400"
                          title="Delete URL"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>

                  {previewingId === entry.id && (entry.content || entry.raw_content) && (
                    <div className="mt-4 flex-1 min-h-0 flex flex-col">
                      <div className="flex justify-between items-center flex-shrink-0">
                        <button
                          onClick={() => toggleContentVersion(entry.id)}
                          className="text-sm text-gray-300 hover:text-gray-100"
                        >
                          {showRawContent[entry.id] ? 'Show Processed Content' : 'Show Raw Content'}
                        </button>
                      </div>
                      <div className="mt-2 flex-1 bg-gray-800 rounded-lg p-4 overflow-y-auto overflow-x-hidden whitespace-pre-wrap">
                        <MarkdownMessage
                          content={showRawContent[entry.id] ? entry.raw_content! : entry.content!}
                          isAssistant={true}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default URLManager; 