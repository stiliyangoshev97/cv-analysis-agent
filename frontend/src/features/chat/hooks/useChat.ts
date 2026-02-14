/**
 * @fileoverview Chat hooks for React Query.
 *
 * Provides hooks for RAG-powered CV chat functionality:
 * - Ask questions about CVs
 * - Get/clear chat history
 * - Explain criterion scores
 * - Compare multiple CVs
 *
 * @module features/chat/hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/shared/components/ui';
import {
  askQuestion,
  getChatHistory,
  clearChatHistory,
  explainCriterion,
  compareCVs,
} from '../api';

// =============================================================================
// Query Keys
// =============================================================================

/** Query keys for chat */
export const chatKeys = {
  all: ['chat'] as const,
  history: (cvId: string) => [...chatKeys.all, 'history', cvId] as const,
  explain: (cvId: string, criterion: string) =>
    [...chatKeys.all, 'explain', cvId, criterion] as const,
};

// =============================================================================
// Chat History Hooks
// =============================================================================

/**
 * Hook to fetch chat history for a CV.
 *
 * @param cvId - UUID of the CV
 * @param limit - Optional max messages
 * @returns Query result with chat history
 *
 * @example
 * ```tsx
 * const { data: history } = useChatHistory('cv-uuid');
 * ```
 */
export const useChatHistory = (cvId: string, limit?: number) => {
  return useQuery({
    queryKey: chatKeys.history(cvId),
    queryFn: () => getChatHistory(cvId, limit),
    enabled: !!cvId,
    staleTime: 1000 * 60, // 1 minute
  });
};

/**
 * Hook to ask a question about a CV.
 *
 * @returns Mutation for asking questions
 *
 * @example
 * ```tsx
 * const { mutate: ask, isPending } = useAskQuestion();
 * ask({ cvId: 'uuid', message: 'What is their experience?' });
 * ```
 */
export const useAskQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ cvId, message }: { cvId: string; message: string }) =>
      askQuestion(cvId, message),
    onSuccess: (_data, variables) => {
      // Invalidate chat history to include new message
      queryClient.invalidateQueries({ queryKey: chatKeys.history(variables.cvId) });
    },
    onError: (error) => {
      toast.error('Failed to get response', error.message);
    },
  });
};

/**
 * Hook to clear chat history for a CV.
 *
 * @returns Mutation for clearing history
 *
 * @example
 * ```tsx
 * const { mutate: clear } = useClearChatHistory();
 * clear('cv-uuid');
 * ```
 */
export const useClearChatHistory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cvId: string) => clearChatHistory(cvId),
    onSuccess: (_, cvId) => {
      queryClient.setQueryData(chatKeys.history(cvId), {
        cv_id: cvId,
        messages: [],
        total: 0,
      });
      toast.success('Chat history cleared');
    },
    onError: (error) => {
      toast.error('Failed to clear chat', error.message);
    },
  });
};

// =============================================================================
// Explain Criterion Hook
// =============================================================================

/**
 * Hook to explain a criterion score.
 *
 * @returns Mutation for explaining criteria
 *
 * @example
 * ```tsx
 * const { mutate: explain, data } = useExplainCriterion();
 * explain({ cvId: 'uuid', criterion: 'Technical Skills' });
 * ```
 */
export const useExplainCriterion = () => {
  return useMutation({
    mutationFn: ({
      cvId,
      criterion,
      includeCvEvidence = true,
    }: {
      cvId: string;
      criterion: string;
      includeCvEvidence?: boolean;
    }) => explainCriterion(cvId, criterion, includeCvEvidence),
    onError: (error) => {
      toast.error('Failed to explain criterion', error.message);
    },
  });
};

// =============================================================================
// Compare CVs Hook
// =============================================================================

/**
 * Hook to compare multiple CVs.
 *
 * @returns Mutation for comparing CVs
 *
 * @example
 * ```tsx
 * const { mutate: compare, data } = useCompareCVs();
 * compare({ cvIds: ['cv1', 'cv2'], question: 'Compare experience' });
 * ```
 */
export const useCompareCVs = () => {
  return useMutation({
    mutationFn: ({
      cvIds,
      question,
    }: {
      cvIds: string[];
      question?: string;
    }) => compareCVs(cvIds, question),
    onError: (error) => {
      toast.error('Failed to compare CVs', error.message);
    },
  });
};
