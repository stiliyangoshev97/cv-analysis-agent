/**
 * @fileoverview Central type exports for the application.
 *
 * All types are now inferred from Zod schemas for consistency.
 * This file re-exports types from schemas for backward compatibility.
 *
 * @module shared/types
 * @see {@link ../schemas/index.ts} for schema definitions
 *
 * @example
 * ```typescript
 * import type { User, CVResult } from '@/shared/types';
 * ```
 */

// =============================================================================
// Re-export all types from schemas (single source of truth)
// =============================================================================

export type {
  // CV Types
  PassFailStatus,
  EvaluationCriteria,
  CVEvaluationResponse,
  UploadResponse,
  ErrorResponse,
  UploadProgress,
  CVResult,
  // Auth Types
  AuthProvider,
  User,
  TokenResponse,
  AuthResponse,
  RegisterRequest,
  LoginRequest,
  RefreshTokenRequest,
  GoogleAuthRequest,
} from '../schemas';
