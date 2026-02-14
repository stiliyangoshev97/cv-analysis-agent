/**
 * @fileoverview Chat API functions.
 *
 * Provides functions for RAG-powered CV chat:
 * - Ask questions about CVs
 * - Get chat history
 * - Explain criterion scores
 * - Compare multiple CVs
 *
 * @module features/chat/api
 */

import { apiClient } from '@/shared/api';
import type {
  ChatMessageRequest,
  AskResponse,
  ChatHistoryResponse,
  ExplainCriterionResponse,
  CompareRequest,
  CompareResponse,
} from '@/shared/types';

// =============================================================================
// Chat with CV
// =============================================================================

/**
 * Ask a question about a specific CV using RAG.
 *
 * @param cvId - UUID of the CV to ask about
 * @param message - The question to ask
 * @returns Promise resolving to the assistant's response
 *
 * @example
 * ```typescript
 * const response = await askQuestion('cv-uuid', 'What is their Python experience?');
 * console.log(response.message.content);
 * ```
 */
export const askQuestion = async (
  cvId: string,
  message: string
): Promise<AskResponse> => {
  const body: ChatMessageRequest = { message };
  const response = await apiClient.post<AskResponse>(`/api/chat/${cvId}`, body);
  return response.data;
};

/**
 * Get chat history for a CV.
 *
 * @param cvId - UUID of the CV
 * @param limit - Optional max messages to return
 * @returns Promise resolving to chat history
 *
 * @example
 * ```typescript
 * const history = await getChatHistory('cv-uuid');
 * history.messages.forEach(msg => console.log(msg.content));
 * ```
 */
export const getChatHistory = async (
  cvId: string,
  limit?: number
): Promise<ChatHistoryResponse> => {
  const params = limit ? { limit } : {};
  const response = await apiClient.get<ChatHistoryResponse>(`/api/chat/${cvId}`, { params });
  return response.data;
};

/**
 * Clear chat history for a CV.
 *
 * @param cvId - UUID of the CV
 * @returns Promise resolving to confirmation
 *
 * @example
 * ```typescript
 * await clearChatHistory('cv-uuid');
 * ```
 */
export const clearChatHistory = async (cvId: string): Promise<{ message: string }> => {
  const response = await apiClient.delete<{ message: string }>(`/api/chat/${cvId}`);
  return response.data;
};

// =============================================================================
// Explain Criterion
// =============================================================================

/**
 * Get detailed explanation for a criterion score.
 *
 * @param cvId - UUID of the CV
 * @param criterion - Name of the criterion (e.g., "Technical Skills")
 * @param includeCvEvidence - Whether to include CV excerpts
 * @returns Promise resolving to explanation
 *
 * @example
 * ```typescript
 * const explanation = await explainCriterion('cv-uuid', 'Technical Skills');
 * console.log(explanation.explanation);
 * console.log(explanation.evidence);
 * ```
 */
export const explainCriterion = async (
  cvId: string,
  criterion: string,
  includeCvEvidence: boolean = true
): Promise<ExplainCriterionResponse> => {
  const response = await apiClient.post<ExplainCriterionResponse>(
    `/api/chat/${cvId}/explain/${encodeURIComponent(criterion)}`,
    { include_cv_evidence: includeCvEvidence }
  );
  return response.data;
};

// =============================================================================
// Compare CVs
// =============================================================================

/**
 * Compare multiple CVs against each other.
 *
 * @param cvIds - Array of 2-5 CV UUIDs to compare
 * @param question - Comparison question or focus area
 * @returns Promise resolving to comparison analysis
 *
 * @example
 * ```typescript
 * const comparison = await compareCVs(['cv1', 'cv2'], 'Compare their fintech experience');
 * console.log(comparison.comparison);
 * console.log(comparison.ranking);
 * ```
 */
export const compareCVs = async (
  cvIds: string[],
  question: string = 'Compare these candidates overall'
): Promise<CompareResponse> => {
  const body: CompareRequest = { cv_ids: cvIds, question };
  const response = await apiClient.post<CompareResponse>('/api/chat/compare', body);
  return response.data;
};
