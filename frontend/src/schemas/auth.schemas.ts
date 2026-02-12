/**
 * @fileoverview Auth Zod schemas with type inference.
 *
 * Defines all authentication-related data contracts.
 * Types are inferred from schemas - single source of truth pattern.
 *
 * @module schemas/auth.schemas
 * @see {@link https://zod.dev/ Zod Documentation}
 */

import { z } from 'zod';

// =============================================================================
// Enums
// =============================================================================

/**
 * Authentication provider enum.
 *
 * Identifies how the user authenticated.
 *
 * @example
 * ```typescript
 * const provider: AuthProvider = 'google';
 * ```
 */
export const authProviderSchema = z.enum(['email', 'google']);

// =============================================================================
// User Schema
// =============================================================================

/**
 * User schema matching backend response.
 *
 * Contains public user information (no sensitive data).
 *
 * @example
 * ```typescript
 * const user: User = {
 *   id: 'usr_abc123',
 *   email: 'user@example.com',
 *   full_name: 'John Doe',
 *   auth_provider: 'email',
 *   avatar_url: null,
 *   created_at: '2025-02-12T10:30:00Z'
 * };
 * ```
 */
export const userSchema = z.object({
  /** Unique user identifier */
  id: z.string(),
  /** User's email address */
  email: z.string().email(),
  /** User's display name */
  full_name: z.string(),
  /** How the user authenticated */
  auth_provider: authProviderSchema,
  /** Profile picture URL, null if not set */
  avatar_url: z.string().url().nullable(),
  /** ISO 8601 timestamp of account creation */
  created_at: z.string(),
});

// =============================================================================
// Token Schemas
// =============================================================================

/**
 * Token response schema.
 *
 * Contains JWT tokens for authentication.
 *
 * @example
 * ```typescript
 * const tokens: TokenResponse = {
 *   access_token: 'eyJhbGciOi...',
 *   refresh_token: 'eyJhbGciOi...',
 *   token_type: 'bearer',
 *   expires_in: 1800
 * };
 * ```
 */
export const tokenResponseSchema = z.object({
  /** JWT access token for API authentication */
  access_token: z.string(),
  /** JWT refresh token for getting new access tokens */
  refresh_token: z.string(),
  /** Token type, always 'bearer' */
  token_type: z.string().default('bearer'),
  /** Access token expiration in seconds */
  expires_in: z.number(),
});

// =============================================================================
// Auth Response Schema
// =============================================================================

/**
 * Full authentication response schema.
 *
 * Returned on successful login or registration.
 */
export const authResponseSchema = z.object({
  /** User data */
  user: userSchema,
  /** Authentication tokens */
  tokens: tokenResponseSchema,
});

// =============================================================================
// Request Schemas
// =============================================================================

/**
 * Registration request schema.
 *
 * Validates user input for registration form.
 */
export const registerRequestSchema = z.object({
  /** Valid email address */
  email: z.string().email('Please enter a valid email address'),
  /** Password with minimum 8 characters */
  password: z.string().min(8, 'Password must be at least 8 characters'),
  /** Full name, 2-100 characters */
  full_name: z.string().min(2, 'Name must be at least 2 characters').max(100),
});

/**
 * Login request schema.
 *
 * Validates user input for login form.
 */
export const loginRequestSchema = z.object({
  /** Email address */
  email: z.string().email('Please enter a valid email address'),
  /** Password */
  password: z.string().min(1, 'Password is required'),
});

/**
 * Refresh token request schema.
 */
export const refreshTokenRequestSchema = z.object({
  /** The refresh token to exchange */
  refresh_token: z.string(),
});

/**
 * Google OAuth request schema.
 *
 * For exchanging Google auth code for tokens.
 */
export const googleAuthRequestSchema = z.object({
  /** Authorization code from Google OAuth */
  code: z.string(),
  /** Redirect URI used in OAuth flow */
  redirect_uri: z.string().url(),
});

// =============================================================================
// Inferred Types
// =============================================================================

/** Authentication provider type */
export type AuthProvider = z.infer<typeof authProviderSchema>;

/** User data type */
export type User = z.infer<typeof userSchema>;

/** Token response type */
export type TokenResponse = z.infer<typeof tokenResponseSchema>;

/** Full auth response type */
export type AuthResponse = z.infer<typeof authResponseSchema>;

/** Registration request type */
export type RegisterRequest = z.infer<typeof registerRequestSchema>;

/** Login request type */
export type LoginRequest = z.infer<typeof loginRequestSchema>;

/** Refresh token request type */
export type RefreshTokenRequest = z.infer<typeof refreshTokenRequestSchema>;

/** Google OAuth request type */
export type GoogleAuthRequest = z.infer<typeof googleAuthRequestSchema>;
