/**
 * @fileoverview useCVList Hook
 *
 * React hook for fetching the user's list of CVs.
 * Uses TanStack Query for caching and state management.
 *
 * @module features/cv/hooks/useCVList
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useCVList();
 * 
 * if (data) {
 *   data.cvs.forEach(cv => console.log(cv.candidate_name));
 * }
 * ```
 */

import { useQuery } from '@tanstack/react-query';
import { listCVs } from '../api';

/** Query keys for CV list */
export const cvKeys = {
  all: ['cvs'] as const,
  list: (limit: number, offset: number) => [...cvKeys.all, 'list', { limit, offset }] as const,
};

/**
 * Hook to fetch the user's list of CVs.
 *
 * @param limit - Maximum number of CVs to return (default 100 for compare modal)
 * @param offset - Number of CVs to skip (default 0)
 * @returns Query result with CV list
 *
 * @example
 * ```tsx
 * const { data: cvList, isLoading } = useCVList();
 * ```
 */
export const useCVList = (limit: number = 100, offset: number = 0) => {
  return useQuery({
    queryKey: cvKeys.list(limit, offset),
    queryFn: () => listCVs(limit, offset),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};
