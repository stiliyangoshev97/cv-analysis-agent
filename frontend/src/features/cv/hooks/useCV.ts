/**
 * @fileoverview useCV Hook
 *
 * React hook for fetching detailed CV information.
 * Uses TanStack Query for caching and state management.
 *
 * @module features/cv/hooks/useCV
 *
 * @example
 * ```tsx
 * const { data: cv, isLoading, error } = useCV('cv-uuid');
 * 
 * if (cv) {
 *   console.log(cv.candidate_name, cv.evaluation?.score);
 * }
 * ```
 */

import { useQuery } from '@tanstack/react-query';
import { getCV } from '../api';
import { cvKeys } from './useCVList';

/**
 * Hook to fetch detailed CV information.
 *
 * @param cvId - The UUID of the CV to fetch
 * @returns Query result with CV details
 *
 * @example
 * ```tsx
 * const { data: cv, isLoading } = useCV('cv-uuid');
 * ```
 */
export const useCV = (cvId: string) => {
  return useQuery({
    queryKey: [...cvKeys.all, 'detail', cvId],
    queryFn: () => getCV(cvId),
    enabled: !!cvId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};
