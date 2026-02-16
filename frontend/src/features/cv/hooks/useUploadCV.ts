/**
 * @fileoverview useUploadCV Hook
 *
 * React hook for CV file upload with progress tracking.
 * Uses TanStack Query mutation for state management.
 *
 * @module features/cv/hooks/useUploadCV
 *
 * FEATURES:
 * - File upload with progress tracking
 * - Loading state management
 * - Error handling
 * - Automatic progress reset on completion
 *
 * @example
 * ```tsx
 * const { upload, isUploading, progress, error, reset } = useUploadCV();
 *
 * const handleFileSelect = (file: File) => {
 *   upload(file, {
 *     onSuccess: (data) => {
 *       console.log('Upload complete:', data);
 *     },
 *     onError: (error) => {
 *       console.error('Upload failed:', error);
 *     },
 *   });
 * };
 * ```
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { uploadCV } from '../api';
import { toast } from '@/shared/components/ui';
import { cvKeys } from './useCVList';
import type { UploadProgress, UploadResponse } from '@/shared/types';

/**
 * Upload parameters for CV mutation.
 */
interface UploadParams {
  file: File;
  templateId: string;
}

/**
 * Hook return type for useUploadCV.
 */
interface UseUploadCVReturn {
  /** Function to trigger file upload */
  upload: (
    params: UploadParams,
    options?: { onSuccess?: (data: UploadResponse) => void; onError?: (error: Error) => void }
  ) => void;
  /** Whether upload is in progress */
  isUploading: boolean;
  /** Current upload progress (null when not uploading) */
  progress: UploadProgress | null;
  /** Error from failed upload */
  error: Error | null;
  /** Response data from successful upload */
  data: UploadResponse | undefined;
  /** Reset mutation state */
  reset: () => void;
}

/**
 * useUploadCV Hook
 *
 * Manages CV file upload with progress tracking and state management.
 *
 * @returns Upload function, loading state, progress, and error state
 */
export const useUploadCV = (): UseUploadCVReturn => {
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const queryClient = useQueryClient();

  const mutation = useMutation<UploadResponse, Error, UploadParams>({
    mutationFn: ({ file, templateId }: UploadParams) =>
      uploadCV(file, templateId, setProgress),
    onMutate: () => {
      setProgress({ loaded: 0, total: 0, percentage: 0 });
    },
    onSuccess: (data) => {
      if (data.success && data.evaluation) {
        const status = data.evaluation.status === 'pass' ? 'passed' : 'failed';
        toast.success('CV Evaluated', `${data.evaluation.candidate_name || 'Candidate'} ${status} with ${data.evaluation.match_score}% match`);
        
        // Invalidate CV list cache so history page updates immediately
        queryClient.invalidateQueries({ queryKey: cvKeys.all });
      }
    },
    onError: (error) => {
      toast.error('Upload failed', error.message);
    },
    onSettled: () => {
      setProgress(null);
    },
  });

  return {
    upload: mutation.mutate,
    isUploading: mutation.isPending,
    progress,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
};
