/**
 * @fileoverview CV feature API functions.
 *
 * Provides API calls for CV upload and evaluation.
 *
 * @module features/cv/api
 */

import { apiClient } from '@/shared/api';
import type { UploadResponse, UploadProgress, CVListResponse } from '@/shared/types';

/**
 * Get a paginated list of the user's CVs.
 *
 * @param limit - Maximum number of CVs to return (default 20)
 * @param offset - Number of CVs to skip (default 0)
 * @returns Promise resolving to paginated CV list
 *
 * @example
 * ```typescript
 * const { cvs, total } = await listCVs(20, 0);
 * cvs.forEach(cv => console.log(cv.candidate_name));
 * ```
 */
export const listCVs = async (
  limit: number = 20,
  offset: number = 0
): Promise<CVListResponse> => {
  const response = await apiClient.get<CVListResponse>('/api/cv/', {
    params: { limit, offset },
  });
  return response.data;
};

/**
 * Upload a CV file for AI evaluation.
 *
 * Sends the PDF to the backend for text extraction and Claude AI evaluation.
 * Supports progress tracking for large files.
 *
 * @param file - The PDF file to upload
 * @param onProgress - Optional callback for upload progress updates
 * @returns Promise resolving to the evaluation response
 *
 * @example
 * ```typescript
 * const response = await uploadCV(file, (progress) => {
 *   console.log(`${progress.percentage}% uploaded`);
 * });
 *
 * if (response.success && response.evaluation) {
 *   console.log(`Score: ${response.evaluation.match_score}`);
 * }
 * ```
 *
 * @throws {AxiosError} On network errors or server errors
 */
export const uploadCV = async (
  file: File,
  templateId: string,
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<UploadResponse>(
    `/api/cv/upload?template_id=${templateId}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      },
    }
  );

  return response.data;
};

/**
 * Check CV service health status.
 *
 * Useful for verifying the backend is running and AI is configured.
 *
 * @returns Promise resolving to health check response
 *
 * @example
 * ```typescript
 * const health = await checkHealth();
 * if (health.ai_configured) {
 *   console.log('AI is ready!');
 * }
 * ```
 */
export const checkHealth = async (): Promise<{ status: string; ai_configured: boolean }> => {
  const response = await apiClient.get('/api/cv/health');
  return response.data;
};
