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

import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import { uploadCV } from '../api';
import type { UploadProgress, UploadResponse } from '@/shared/types';

/**
 * Hook return type for useUploadCV.
 */
interface UseUploadCVReturn {
  /** Function to trigger file upload */
  upload: typeof useMutation<UploadResponse, Error, File>['prototype']['mutate'];
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

  const mutation = useMutation<UploadResponse, Error, File>({
    mutationFn: (file: File) => uploadCV(file, setProgress),
    onMutate: () => {
      setProgress({ loaded: 0, total: 0, percentage: 0 });
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
