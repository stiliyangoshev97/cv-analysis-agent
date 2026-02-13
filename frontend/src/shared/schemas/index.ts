/**
 * @fileoverview Central export for all Zod schemas.
 *
 * Import schemas and types from this file for consistency.
 *
 * @module schemas
 *
 * @example
 * ```typescript
 * import { userSchema, type User } from '@/schemas';
 *
 * const user = userSchema.parse(apiResponse);
 * ```
 */

// CV Evaluation Schemas
export {
  // Schemas
  passFailStatusSchema,
  evaluationCriteriaSchema,
  cvEvaluationResponseSchema,
  uploadResponseSchema,
  errorResponseSchema,
  uploadProgressSchema,
  cvResultSchema,
  // Types
  type PassFailStatus,
  type EvaluationCriteria,
  type CVEvaluationResponse,
  type UploadResponse,
  type ErrorResponse,
  type UploadProgress,
  type CVResult,
} from './cv.schemas';

// Auth Schemas
export {
  // Schemas
  authProviderSchema,
  userSchema,
  tokenResponseSchema,
  authResponseSchema,
  registerRequestSchema,
  loginRequestSchema,
  refreshTokenRequestSchema,
  googleAuthRequestSchema,
  // Types
  type AuthProvider,
  type User,
  type TokenResponse,
  type AuthResponse,
  type RegisterRequest,
  type LoginRequest,
  type RefreshTokenRequest,
  type GoogleAuthRequest,
} from './auth.schemas';

// Notification Schemas
export {
  // Schemas
  notificationSettingsSchema,
  notificationSettingsUpdateSchema,
  notificationChannelSchema,
  sendTestNotificationRequestSchema,
  notificationResultSchema,
  notificationServiceStatusSchema,
  // Types
  type NotificationSettings,
  type NotificationSettingsUpdate,
  type NotificationChannel,
  type SendTestNotificationRequest,
  type NotificationResult,
  type NotificationServiceStatus,
} from './notification.schemas';
