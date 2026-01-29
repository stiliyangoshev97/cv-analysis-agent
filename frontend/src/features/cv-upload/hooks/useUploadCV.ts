import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import { uploadCV } from '../../../lib/api';
import type { UploadProgress, UploadResponse } from '../../../types';

export const useUploadCV = () => {
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
