import { apiClient } from '../../../lib/api';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
  GoogleAuthRequest,
  TokenResponse,
  User,
} from '../../../types';

/**
 * Register a new user with email/password
 */
export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/auth/register', data);
  return response.data;
};

/**
 * Login with email/password
 */
export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/auth/login', data);
  return response.data;
};

/**
 * Refresh access token using refresh token
 */
export const refreshToken = async (data: RefreshTokenRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/api/auth/refresh', data);
  return response.data;
};

/**
 * Authenticate with Google OAuth
 */
export const googleAuth = async (data: GoogleAuthRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/auth/google', data);
  return response.data;
};

/**
 * Get current user profile
 */
export const getMe = async (): Promise<User> => {
  const response = await apiClient.get<User>('/api/auth/me');
  return response.data;
};

/**
 * Logout (server-side acknowledgement)
 */
export const logout = async (): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/api/auth/logout');
  return response.data;
};
