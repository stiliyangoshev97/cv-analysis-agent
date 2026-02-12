/**
 * @fileoverview Authentication API functions.
 *
 * Provides functions for all auth-related API calls:
 * - User registration
 * - User login
 * - Token refresh
 * - Google OAuth
 * - User profile
 *
 * @module features/auth/api
 */

import { apiClient } from '@/shared/api';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
  GoogleAuthRequest,
  TokenResponse,
  User,
} from '@/shared/types';

/**
 * Register a new user with email and password.
 *
 * Creates a new account and returns authentication tokens.
 * User is automatically logged in after successful registration.
 *
 * @param data - Registration data with email, password, and full name
 * @returns Promise resolving to auth response with user and tokens
 *
 * @example
 * ```typescript
 * const response = await register({
 *   email: 'user@example.com',
 *   password: 'securepassword123',
 *   full_name: 'John Doe'
 * });
 * console.log(`Welcome, ${response.user.full_name}!`);
 * ```
 *
 * @throws {AxiosError} 400 if email already registered
 */
export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/auth/register', data);
  return response.data;
};

/**
 * Login with email and password.
 *
 * Authenticates user credentials and returns tokens for session.
 *
 * @param data - Login credentials
 * @returns Promise resolving to auth response with user and tokens
 *
 * @example
 * ```typescript
 * const response = await login({
 *   email: 'user@example.com',
 *   password: 'securepassword123'
 * });
 * // Store tokens for subsequent requests
 * localStorage.setItem('token', response.tokens.access_token);
 * ```
 *
 * @throws {AxiosError} 401 if credentials are invalid
 */
export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/auth/login', data);
  return response.data;
};

/**
 * Refresh access token using a valid refresh token.
 *
 * Called when the access token expires to get a new one
 * without requiring the user to login again.
 *
 * @param data - Object containing the refresh token
 * @returns Promise resolving to new token pair
 *
 * @example
 * ```typescript
 * const tokens = await refreshToken({
 *   refresh_token: storedRefreshToken
 * });
 * // Update stored tokens
 * authStore.setTokens(tokens);
 * ```
 *
 * @throws {AxiosError} 401 if refresh token is invalid or expired
 */
export const refreshToken = async (data: RefreshTokenRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/api/auth/refresh', data);
  return response.data;
};

/**
 * Authenticate with Google OAuth.
 *
 * Exchanges a Google authorization code for application tokens.
 * Creates a new account if the user doesn't exist.
 *
 * @param data - Google auth code and redirect URI
 * @returns Promise resolving to auth response with user and tokens
 *
 * @example
 * ```typescript
 * // After Google OAuth redirect
 * const response = await googleAuth({
 *   code: authorizationCode,
 *   redirect_uri: 'http://localhost:5173/auth/callback'
 * });
 * ```
 *
 * @throws {AxiosError} 400 if Google auth not configured or code invalid
 */
export const googleAuth = async (data: GoogleAuthRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/auth/google', data);
  return response.data;
};

/**
 * Get current authenticated user's profile.
 *
 * Requires a valid access token in the Authorization header.
 * Used to verify token validity and get user data.
 *
 * @returns Promise resolving to user profile data
 *
 * @example
 * ```typescript
 * const user = await getMe();
 * console.log(`Logged in as ${user.email}`);
 * ```
 *
 * @throws {AxiosError} 401 if not authenticated or token expired
 */
export const getMe = async (): Promise<User> => {
  const response = await apiClient.get<User>('/api/auth/me');
  return response.data;
};

/**
 * Logout the current user.
 *
 * Notifies the server of logout. Client should also clear stored tokens.
 * Note: With JWT, tokens remain valid until expiry - this is a best-effort logout.
 *
 * @returns Promise resolving to success message
 *
 * @example
 * ```typescript
 * await logout();
 * authStore.clearAuth();
 * navigate('/login');
 * ```
 */
export const logout = async (): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/api/auth/logout');
  return response.data;
};
