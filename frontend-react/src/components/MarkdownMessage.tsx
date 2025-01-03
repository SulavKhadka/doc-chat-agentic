import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownMessageProps {
  content: string;
  isAssistant: boolean;
}

const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ content, isAssistant }) => {
  const [showMarkdown, setShowMarkdown] = useState(true);

  const toggleMarkdown = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowMarkdown(!showMarkdown);
  };

  return (
    <div className={`mb-4 ${isAssistant ? 'text-left' : 'text-right'}`}>
      <div
        className={`relative inline-block p-3 rounded-lg ${
          isAssistant 
            ? 'bg-gray-800 text-gray-100' 
            : 'bg-indigo-600 text-gray-100'
        }`}
      >
        <div className="prose prose-sm prose-invert max-w-none">
          {showMarkdown ? (
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              className={`${isAssistant ? 'text-gray-100' : 'text-gray-100'} 
                         [&_a]:text-indigo-400 [&_code]:text-teal-300 
                         [&_pre]:bg-gray-900/50 [&_blockquote]:border-l-gray-600
                         [&_table_th]:border-gray-700 [&_table_td]:border-gray-700`}
            >
              {content}
            </ReactMarkdown>
          ) : (
            <pre className="whitespace-pre-wrap font-sans text-sm text-gray-100">{content}</pre>
          )}
        </div>
        
        {isAssistant && (
          <button
            onClick={toggleMarkdown}
            className="absolute bottom-1 right-1 p-1 rounded-full 
                     bg-gray-700 hover:bg-gray-600 transition-colors"
            title={showMarkdown ? "Show plain text" : "Show markdown"}
          >
            <svg
              className="w-3 h-3 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {showMarkdown ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"
                />
              )}
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default MarkdownMessage; 