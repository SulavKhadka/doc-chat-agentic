import React, { useState } from 'react';
import MarkdownMessage from './MarkdownMessage';

interface URLEntry {
  id: string;
  url: string;
  status: 'pending' | 'loading' | 'complete' | 'error';
  conversation_id: string;
  content?: string;
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
    setPreviewingId(previewingId === entry.id ? null : entry.id);
  };

  return (
    <div className={`border-t border-gray-700 ${previewingId ? 'h-[600px] flex flex-col' : ''}`}>
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
        <div className={`bg-gray-800 border-t border-gray-700 ${previewingId ? 'flex-1 flex flex-col min-h-0' : ''}`}>
          <form onSubmit={handleSubmit} className="p-4 border-b border-gray-700">
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

          <div className={`${previewingId ? 'flex-1 flex flex-col min-h-0' : ''} p-4`}>
            <div className={`space-y-2 ${previewingId ? 'h-full flex flex-col min-h-0' : 'max-h-60'} overflow-y-auto`}>
              {urls.map((entry) => (
                <div
                  key={entry.id}
                  className={`p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow
                            ${previewingId === entry.id ? 'flex-1 flex flex-col min-h-0' : ''}`}
                >
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

                  {/* Content Preview */}
                  {previewingId === entry.id && entry.content && (
                    <div className="mt-3 border-t border-gray-600 pt-3 flex-1 min-h-0 overflow-y-auto">
                      <div className="prose prose-invert max-w-none">
                        <MarkdownMessage
                          content={entry.content}
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