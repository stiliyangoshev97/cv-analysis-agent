/**
 * @fileoverview Chat Panel Component
 *
 * Slide-out panel for chatting with AI about a CV.
 * Includes message history, input field, and send button.
 *
 * @module features/chat/components/ChatPanel
 */

import { useState, useRef, useEffect } from 'react';
import { Button, Input, Text, Heading, Spinner } from '@/shared/components';
import { useChatHistory, useAskQuestion, useClearChatHistory } from '../hooks';
import { ChatMessage } from './ChatMessage';

interface ChatPanelProps {
  /** CV ID to chat about */
  cvId: string;
  /** CV candidate name for display */
  candidateName?: string;
  /** Whether the panel is open */
  isOpen: boolean;
  /** Callback to close the panel */
  onClose: () => void;
}

/**
 * Chat Panel Component
 *
 * Full chat interface for asking questions about a CV.
 *
 * @example
 * ```tsx
 * <ChatPanel
 *   cvId="uuid"
 *   candidateName="John Doe"
 *   isOpen={showChat}
 *   onClose={() => setShowChat(false)}
 * />
 * ```
 */
export const ChatPanel = ({
  cvId,
  candidateName,
  isOpen,
  onClose,
}: ChatPanelProps) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { data: history, isLoading: isLoadingHistory } = useChatHistory(cvId);
  const { mutate: askQuestion, isPending: isAsking } = useAskQuestion();
  const { mutate: clearHistory, isPending: isClearing } = useClearChatHistory();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history?.messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSend = () => {
    if (!inputValue.trim() || isAsking) return;

    askQuestion(
      { cvId, message: inputValue.trim() },
      {
        onSuccess: () => {
          setInputValue('');
        },
      }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    if (confirm('Clear all chat history for this CV?')) {
      clearHistory(cvId);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 z-40"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-white shadow-2xl z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div>
            <Heading level={5} className="text-base">Ask AI</Heading>
            {candidateName && (
              <Text size="sm" color="muted">About {candidateName}</Text>
            )}
          </div>
          <div className="flex items-center gap-2">
            {history && history.messages.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                disabled={isClearing}
                className="text-gray-500"
              >
                Clear
              </Button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoadingHistory ? (
            <div className="flex items-center justify-center py-8">
              <Spinner size="md" />
            </div>
          ) : history?.messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <Text weight="medium" className="mb-1">Start a conversation</Text>
              <Text size="sm" color="muted" className="max-w-xs">
                Ask questions about this CV, like "What's their Python experience?" or "Why did they score low on fintech?"
              </Text>
            </div>
          ) : (
            <>
              {history?.messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isAsking && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Spinner size="sm" />
                      <Text size="sm" color="muted">Thinking...</Text>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              placeholder="Ask about this CV..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isAsking}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={!inputValue.trim() || isAsking}
              isLoading={isAsking}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </Button>
          </div>
          <Text size="xs" color="muted" className="mt-2 text-center">
            Press Enter to send
          </Text>
        </div>
      </div>
    </>
  );
};
