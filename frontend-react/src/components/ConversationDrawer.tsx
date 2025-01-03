import React from 'react';

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  unread?: boolean;
}

interface ConversationDrawerProps {
  conversations: Conversation[];
  selectedId: string | null;
  onSelectConversation: (id: string) => void;
}

const ConversationDrawer: React.FC<ConversationDrawerProps> = ({
  conversations,
  selectedId,
  onSelectConversation,
}) => {
  return (
    <div className="w-80 h-full border-r border-gray-700 bg-gray-800">
      {/* Search Bar */}
      <div className="p-4 border-b border-gray-700">
        <div className="relative">
          <input
            type="text"
            placeholder="Search conversations..."
            className="w-full px-4 py-2 bg-gray-700 rounded-lg 
                     text-gray-100 placeholder-gray-400
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 border-transparent"
          />
          <svg
            className="absolute right-3 top-2.5 h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Conversations List */}
      <div className="overflow-y-auto h-[calc(100%-73px)]">
        {conversations.map((conversation) => (
          <div
            key={conversation.id}
            onClick={() => onSelectConversation(conversation.id)}
            className={`p-4 cursor-pointer transition-colors
              ${
                selectedId === conversation.id 
                  ? 'bg-gray-700' 
                  : 'hover:bg-gray-700/50'
              }`}
          >
            <div className="flex justify-between items-start mb-1">
              <h3 className="font-medium text-gray-100 truncate">
                {conversation.title}
              </h3>
              <span className="text-xs text-gray-400">{conversation.timestamp}</span>
            </div>
            <p className="text-sm text-gray-400 truncate">
              {conversation.lastMessage}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversationDrawer; 