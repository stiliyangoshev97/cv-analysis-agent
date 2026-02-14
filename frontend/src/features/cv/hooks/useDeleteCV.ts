/**
 * @fileoverview useDeleteCV Hook
 *
 * React hook for deleting a CV and all related data.
 * Uses TanStack Query for mutation and cache invalidation.
 *
 * @module features/cv/hooks/useDeleteCV
 *
 * @example
 * ```tsx
 * const { mutate: deleteCV, isPending } = useDeleteCV();
 * 
 * const handleDelete = (cvId: string) => {
 *   deleteCV(cvId, {
 *     onSuccess: () => console.log('CV deleted'),
 *   });
 * };
 * ```
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/shared/components/ui';
import { deleteCV } from '../api';
import { cvKeys } from './useCVList';

/**
 * Hook to delete a CV.
 *
 * Deletes the CV and invalidates the CV list cache to refresh the UI.
 *
 * @returns Mutation for deleting CVs
 *
 * @example
 * ```tsx
 * const { mutate: remove, isPending } = useDeleteCV();
 * remove('cv-uuid');
 * ```
 */
export const useDeleteCV = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cvId: string) => deleteCV(cvId),
    onSuccess: () => {
      // Invalidate all CV list queries to refresh the data
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      toast.success('CV deleted', 'The CV and all related data have been removed.');
    },
    onError: (error: Error) => {
      toast.error('Failed to delete CV', error.message);
    },
  });
};
