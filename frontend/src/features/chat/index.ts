/**
 * @fileoverview Chat feature barrel export
 *
 * Exports all chat-related components, hooks, and API functions.
 *
 * @module features/chat
 */

// Components
export { ChatMessage, ChatPanel, ExplainModal } from './components';

// Hooks
export {
  chatKeys,
  useChatHistory,
  useAskQuestion,
  useClearChatHistory,
  useExplainCriterion,
  useCompareCVs,
} from './hooks';

// API functions
export {
  askQuestion,
  getChatHistory,
  clearChatHistory,
  explainCriterion,
  compareCVs,
} from './api';
