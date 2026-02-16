/**
 * @fileoverview Re-evaluate CV hook.
 *
 * Provides a mutation hook for re-evaluating a CV with a different profile.
 *
 * @module features/cv/hooks/useReEvaluateCV
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/shared/components/ui';
import { reEvaluateCV } from '../api/cv.api';
import { cvKeys } from './useCVList';

/**
 * Hook to re-evaluate a CV with a different evaluation profile.
 *
 * Invalidates the CV detail and list queries on success.
 *
 * @returns Mutation for re-evaluating CVs
 *
 * @example
 * ```tsx
 * const { mutate: reEvaluate, isPending } = useReEvaluateCV();
 * 
 * reEvaluate(
 *   { cvId: 'uuid', templateId: 'template-uuid' },
 *   { onSuccess: () => console.log('Re-evaluated!') }
 * );
 * ```
 */
export const useReEvaluateCV = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ cvId, templateId }: { cvId: string; templateId: string }) =>
      reEvaluateCV(cvId, templateId),
    onSuccess: (data, variables) => {
      // Invalidate CV detail and list queries
      queryClient.invalidateQueries({ queryKey: ['cv', variables.cvId] });
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      
      const score = data.evaluation?.match_score ?? 'N/A';
      toast.success(`CV re-evaluated successfully. New score: ${score}%`);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to re-evaluate CV. Please try again.');
    },
  });
};
