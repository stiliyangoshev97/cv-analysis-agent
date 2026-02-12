// API Response Types - matches backend schemas

export type PassFailStatus = 'pass' | 'fail';

export interface EvaluationCriteria {
  name: string;
  passed: boolean;
  details: string;
}

export interface CVEvaluationResponse {
  status: PassFailStatus;
  match_score: number;
  reasoning: string;
  criteria: EvaluationCriteria[];
  candidate_name: string | null;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  evaluation: CVEvaluationResponse | null;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  detail?: string;
}

// Frontend Types
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface CVResult {
  id: string;
  filename: string;
  evaluation: CVEvaluationResponse;
  uploadedAt: Date;
}

// ============== Auth Types ==============

export type AuthProvider = 'email' | 'google';

export interface User {
  id: string;
  email: string;
  full_name: string;
  auth_provider: AuthProvider;
  avatar_url: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenResponse;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface GoogleAuthRequest {
  code: string;
  redirect_uri: string;
}
