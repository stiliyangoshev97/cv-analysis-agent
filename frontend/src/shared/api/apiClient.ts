/**
 * @fileoverview API client configuration with Axios.
 *
 * Configures Axios with:
 * - Base URL pointing to backend server
 * - Auth token interceptor for authenticated requests
 * - 401 response handler for auto-logout on expired tokens
 *
 * @module shared/api/apiClient
 */

import axios from 'axios';

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
 * import { apiClient } from '@/shared/api';
 * 
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
