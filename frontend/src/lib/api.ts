/**
 * @fileoverview API client configuration and request functions.
 *
 * Configures Axios with:
 * - Base URL pointing to backend server
 * - Auth token interceptor for authenticated requests
 * - 401 response handler for auto-logout on expired tokens
 *
 * @module lib/api
 */

import axios from 'axios';
import type { UploadResponse, UploadProgress } from '../types';

/** Backend API base URL */
const API_BASE_URL = 'http://localhost:8000';

/**
 * Configured Axios instance for API requests.
 *
 * Includes interceptors for:
 * - Automatically attaching auth tokens to requests
 * - Handling 401 responses by clearing auth state
 *
 * @example
 * ```typescript
 * const response = await apiClient.get('/api/cv/health');
 * ```
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Request interceptor: Attach auth token to requests.
 *
 * Reads token from Zustand's localStorage persistence
 * and adds it to the Authorization header.
 */
apiClient.interceptors.request.use((config) => {
  // Get token from localStorage (Zustand persists there)
  const authStorage = localStorage.getItem('cv-agent-auth');
  if (authStorage) {
    try {
      const parsed = JSON.parse(authStorage);
      const accessToken = parsed?.state?.tokens?.access_token;
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
    } catch {
      // Ignore parse errors
    }
  }
  return config;
});

/**
 * Response interceptor: Handle 401 Unauthorized errors.
 *
 * Clears auth state and reloads the page when a 401 is received,
 * forcing the user to re-authenticate.
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear auth state on 401
      localStorage.removeItem('cv-agent-auth');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

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
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<UploadResponse>('/api/cv/upload', formData, {
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
  });

  return response.data;
};

/**
 * Check backend API health status.
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
