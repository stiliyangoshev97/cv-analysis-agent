/**
 * @fileoverview Chat Message Component
 *
 * Displays a single chat message (user or assistant).
 *
 * @module features/chat/components/ChatMessage
 */

import { Text } from '@/shared/components';
import type { ChatMessage as ChatMessageType } from '@/shared/types';

interface ChatMessageProps {
  /** The message to display */
  message: ChatMessageType;
}

/**
 * Chat Message Component
 *
 * Renders a single message with appropriate styling based on role.
 *
 * @example
 * ```tsx
 * <ChatMessage message={message} />
 * ```
 */
export const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-gray-100 text-gray-900 rounded-bl-md'
        }`}
      >
        <Text
          size="sm"
          className={`whitespace-pre-wrap ${isUser ? 'text-white' : 'text-gray-900'}`}
        >
          {message.content}
        </Text>

        {/* Sources (only for assistant messages) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <Text size="xs" color="muted" className="mb-1">
              Sources from CV:
            </Text>
            <ul className="space-y-1">
              {message.sources.slice(0, 3).map((source, i) => (
                <li key={i} className="text-xs text-gray-500 italic truncate">
                  "{source.slice(0, 100)}..."
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
