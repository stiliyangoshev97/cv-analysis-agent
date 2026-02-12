import axios from 'axios';
import type { UploadResponse, UploadProgress } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add auth token to requests
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

// Handle 401 responses (token expired)
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

export const checkHealth = async (): Promise<{ status: string; ai_configured: boolean }> => {
  const response = await apiClient.get('/api/cv/health');
  return response.data;
};
