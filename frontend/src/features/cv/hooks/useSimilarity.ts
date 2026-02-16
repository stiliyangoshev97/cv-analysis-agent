/**
 * @fileoverview React Query hooks for CV similarity and search features.
 *
 * Provides hooks for finding similar CVs, getting rankings, comparing CVs,
 * and semantic search functionality.
 *
 * @module features/cv/hooks/useSimilarity
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  findSimilarCVs,
  getCVRanking,
  compareCVs,
  searchCVs,
} from '../api/cv.api';
import type {
  SimilarCVsResponse,
  CVRankingResponse,
  CVCompareResponse,
  CVSearchResponse,
} from '@/shared/types';

// =============================================================================
// Query Keys
// =============================================================================

export const similarityKeys = {
  all: ['similarity'] as const,
  similar: (cvId: string) => [...similarityKeys.all, 'similar', cvId] as const,
  ranking: (cvId: string) => [...similarityKeys.all, 'ranking', cvId] as const,
  compare: (cvIds: string[]) => [...similarityKeys.all, 'compare', cvIds.join(',')] as const,
  search: (query: string) => [...similarityKeys.all, 'search', query] as const,
};

// =============================================================================
// Hooks
// =============================================================================

/**
 * Hook to find similar CVs.
 *
 * @param cvId - The source CV UUID
 * @param limit - Maximum number of similar CVs (default 5)
 * @param minSimilarity - Minimum similarity threshold (default 0.3)
 * @param enabled - Whether to enable the query (default true)
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useSimilarCVs(cvId, 5, 0.5);
 * ```
 */
export const useSimilarCVs = (
  cvId: string,
  limit: number = 5,
  minSimilarity: number = 0.3,
  enabled: boolean = true
) => {
  return useQuery<SimilarCVsResponse, Error>({
    queryKey: similarityKeys.similar(cvId),
    queryFn: () => findSimilarCVs(cvId, limit, minSimilarity),
    enabled: enabled && !!cvId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get CV ranking/percentile.
 *
 * @param cvId - The CV UUID to rank
 * @param enabled - Whether to enable the query (default true)
 *
 * @example
 * ```tsx
 * const { data: ranking } = useCVRanking(cvId);
 * console.log(`Top ${100 - ranking.percentile}%`);
 * ```
 */
export const useCVRanking = (cvId: string, enabled: boolean = true) => {
  return useQuery<CVRankingResponse, Error>({
    queryKey: similarityKeys.ranking(cvId),
    queryFn: () => getCVRanking(cvId),
    enabled: enabled && !!cvId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to compare multiple CVs.
 *
 * Uses mutation pattern since comparison is an action, not a simple fetch.
 *
 * @example
 * ```tsx
 * const { mutate: compare, data } = useCompareCVs();
 * compare(['uuid1', 'uuid2']);
 * ```
 */
export const useCompareCVs = () => {
  const queryClient = useQueryClient();

  return useMutation<CVCompareResponse, Error, string[]>({
    mutationFn: (cvIds) => compareCVs(cvIds),
    onSuccess: (data, cvIds) => {
      // Cache the comparison result
      queryClient.setQueryData(similarityKeys.compare(cvIds), data);
    },
    onError: (error) => {
      toast.error('Failed to compare CVs', {
        description: error.message,
      });
    },
  });
};

/**
 * Hook for semantic CV search.
 *
 * @param query - Search query string
 * @param limit - Maximum results (default 10)
 * @param minSimilarity - Minimum similarity (default 0)
 * @param enabled - Whether to enable the query
 *
 * @example
 * ```tsx
 * const { data } = useSearchCVs('Python developer', 10, 0, true);
 * ```
 */
export const useSearchCVs = (
  query: string,
  limit: number = 10,
  minSimilarity: number = 0,
  enabled: boolean = true
) => {
  return useQuery<CVSearchResponse, Error>({
    queryKey: similarityKeys.search(query),
    queryFn: () => searchCVs(query, limit, minSimilarity),
    enabled: enabled && query.length >= 3,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook for semantic CV search as a mutation (for on-demand search).
 *
 * Use this when you want to trigger search manually rather than
 * reactively based on query string changes.
 *
 * @example
 * ```tsx
 * const { mutate: search, data, isPending } = useSearchCVsMutation();
 * search({ query: 'Python developer', limit: 10 });
 * ```
 */
export const useSearchCVsMutation = () => {
  return useMutation<
    CVSearchResponse,
    Error,
    { query: string; limit?: number; minSimilarity?: number }
  >({
    mutationFn: ({ query, limit = 10, minSimilarity = 0 }) =>
      searchCVs(query, limit, minSimilarity),
    onError: (error) => {
      toast.error('Search failed', {
        description: error.message,
      });
    },
  });
};
