/**
 * @fileoverview CV feature API functions.
 *
 * Provides API calls for CV upload, evaluation, similarity search, and ranking.
 *
 * @module features/cv/api
 */

import { apiClient } from '@/shared/api';
import type {
  UploadResponse,
  UploadProgress,
  CVListResponse,
  SimilarCVsResponse,
  CVRankingResponse,
  CVCompareResponse,
  CVSearchResponse,
} from '@/shared/types';

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

/**
 * CV Detail response type.
 * 
 * Matches the backend CVDetailResponse schema.
 */
export interface CVDetailResponse {
  id: string;
  filename: string;
  candidate_name: string | null;
  status: string;
  uploaded_at: string;
  original_text: string;
  evaluation: {
    id: string;
    score: number;
    status: string;
    reasoning: string | null;
    criteria_results: Record<string, {
      score: number;
      max_score: number;
      reasoning: string;
      evidence: string[];
    }> | null;
    evaluated_at: string;
  } | null;
}

/**
 * Get detailed information about a specific CV.
 *
 * @param cvId - The UUID of the CV to retrieve
 * @returns Promise resolving to CV detail response
 *
 * @example
 * ```typescript
 * const cv = await getCV('uuid-of-cv');
 * console.log(cv.candidate_name, cv.evaluation?.score);
 * ```
 *
 * @throws {AxiosError} On network errors or if CV not found
 */
export const getCV = async (cvId: string): Promise<CVDetailResponse> => {
  const response = await apiClient.get<CVDetailResponse>(`/api/cv/${cvId}`);
  return response.data;
};

/**
 * Delete a CV and all related data.
 *
 * Removes the CV, evaluations, embeddings, and chat history.
 *
 * @param cvId - The UUID of the CV to delete
 * @returns Promise resolving when deletion is complete
 *
 * @example
 * ```typescript
 * await deleteCV('uuid-of-cv');
 * console.log('CV deleted successfully');
 * ```
 *
 * @throws {AxiosError} On network errors or if CV not found
 */
export const deleteCV = async (cvId: string): Promise<void> => {
  await apiClient.delete(`/api/cv/${cvId}`);
};

// =============================================================================
// Similarity & Search API Functions
// =============================================================================

/**
 * Find CVs similar to a given CV.
 *
 * Uses vector embeddings to find semantically similar candidates.
 *
 * @param cvId - The UUID of the source CV
 * @param limit - Maximum number of similar CVs to return (default 5)
 * @param minSimilarity - Minimum similarity threshold 0-1 (default 0)
 * @returns Promise resolving to similar CVs response
 *
 * @example
 * ```typescript
 * const { similar_cvs } = await findSimilarCVs('uuid', 5, 0.5);
 * similar_cvs.forEach(cv => console.log(`${cv.candidate_name}: ${cv.similarity_score}`));
 * ```
 */
export const findSimilarCVs = async (
  cvId: string,
  limit: number = 5,
  minSimilarity: number = 0.3
): Promise<SimilarCVsResponse> => {
  const response = await apiClient.get<SimilarCVsResponse>(`/api/cv/${cvId}/similar`, {
    params: { limit, min_similarity: minSimilarity },
  });
  return response.data;
};

/**
 * Get ranking/percentile for a CV.
 *
 * Returns how this CV compares to all other CVs by evaluation score.
 *
 * @param cvId - The UUID of the CV to rank
 * @returns Promise resolving to CV ranking response
 *
 * @example
 * ```typescript
 * const ranking = await getCVRanking('uuid');
 * console.log(`Ranked #${ranking.rank} of ${ranking.total_cvs} (${ranking.label})`);
 * ```
 */
export const getCVRanking = async (cvId: string): Promise<CVRankingResponse> => {
  const response = await apiClient.get<CVRankingResponse>(`/api/cv/${cvId}/ranking`);
  return response.data;
};

/**
 * Compare multiple CVs head-to-head.
 *
 * Returns detailed comparison including similarity matrix and best match.
 *
 * @param cvIds - Array of CV UUIDs to compare (2-10)
 * @returns Promise resolving to CV comparison response
 *
 * @example
 * ```typescript
 * const comparison = await compareCVs(['uuid1', 'uuid2', 'uuid3']);
 * console.log(`Best match: ${comparison.best_match_id}`);
 * ```
 */
export const compareCVs = async (cvIds: string[]): Promise<CVCompareResponse> => {
  const response = await apiClient.post<CVCompareResponse>('/api/cv/compare', {
    cv_ids: cvIds,
  });
  return response.data;
};

/**
 * Search CVs by natural language query.
 *
 * Uses semantic search to find CVs matching the query.
 *
 * @param query - Natural language search query
 * @param limit - Maximum results to return (default 10)
 * @param minSimilarity - Minimum similarity threshold (default 0)
 * @returns Promise resolving to search results
 *
 * @example
 * ```typescript
 * const { results } = await searchCVs('Python developer with fintech experience');
 * results.forEach(cv => console.log(`${cv.candidate_name}: ${cv.similarity_score}`));
 * ```
 */
export const searchCVs = async (
  query: string,
  limit: number = 10,
  minSimilarity: number = 0
): Promise<CVSearchResponse> => {
  const response = await apiClient.post<CVSearchResponse>('/api/cv/search', {
    query,
    limit,
    min_similarity: minSimilarity,
  });
  return response.data;
};

// =============================================================================
// Re-evaluate API Function
// =============================================================================

/**
 * Re-evaluate an existing CV with a different evaluation template.
 *
 * Triggers a new AI evaluation using the specified profile.
 * The previous evaluation is replaced with the new one.
 *
 * @param cvId - The UUID of the CV to re-evaluate
 * @param templateId - The UUID of the new evaluation template to use
 * @returns Promise resolving to the new evaluation response
 *
 * @example
 * ```typescript
 * const result = await reEvaluateCV('cv-uuid', 'template-uuid');
 * if (result.success) {
 *   console.log(`New score: ${result.evaluation.match_score}`);
 * }
 * ```
 *
 * @throws {AxiosError} On network errors or if CV/template not found
 */
export const reEvaluateCV = async (
  cvId: string,
  templateId: string
): Promise<UploadResponse> => {
  const response = await apiClient.post<UploadResponse>(
    `/api/cv/${cvId}/re-evaluate?template_id=${templateId}`
  );
  return response.data;
};

// =============================================================================
// Manual Notification API Function
// =============================================================================

/**
 * Response from manual notification request.
 */
export interface ManualNotifyResponse {
  /** Whether the notification was sent successfully */
  success: boolean;
  /** The channel used (email or whatsapp) */
  channel: 'email' | 'whatsapp';
  /** Success or error message */
  message: string;
}

/**
 * Send a manual notification for a CV evaluation.
 *
 * Allows sending email or WhatsApp notifications on-demand,
 * regardless of automatic notification settings.
 *
 * @param cvId - The UUID of the CV to send notification for
 * @param channel - The notification channel ('email' or 'whatsapp')
 * @returns Promise resolving to the notification response
 *
 * @example
 * ```typescript
 * const result = await sendManualNotification('cv-uuid', 'email');
 * if (result.success) {
 *   console.log('Notification sent!');
 * }
 * ```
 *
 * @throws {AxiosError} On network errors or if channel not configured
 */
export const sendManualNotification = async (
  cvId: string,
  channel: 'email' | 'whatsapp'
): Promise<ManualNotifyResponse> => {
  const response = await apiClient.post<ManualNotifyResponse>(
    `/api/cv/${cvId}/notify`,
    { channel }
  );
  return response.data;
};
