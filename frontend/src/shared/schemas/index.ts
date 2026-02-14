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

// Settings Schemas
export {
  // Schemas
  aiProviderSchema,
  llmProviderSchema,
  apiKeyInfoSchema,
  apiKeyListResponseSchema,
  setApiKeyRequestSchema,
  setApiKeyResponseSchema,
  validateKeyRequestSchema,
  validateKeyResponseSchema,
  agentConfigResponseSchema,
  updateAgentConfigRequestSchema,
  modelOptionSchema,
  providerModelsSchema,
  availableModelsResponseSchema,
  setupStatusResponseSchema,
  // Types
  type AIProvider,
  type LLMProvider,
  type ApiKeyInfo,
  type ApiKeyListResponse,
  type SetApiKeyRequest,
  type SetApiKeyResponse,
  type ValidateKeyRequest,
  type ValidateKeyResponse,
  type AgentConfigResponse,
  type UpdateAgentConfigRequest,
  type ModelOption,
  type ProviderModels,
  type AvailableModelsResponse,
  type SetupStatusResponse,
} from './settings.schemas';

// Chat Schemas
export {
  // Schemas
  chatMessageSchema,
  chatMessageRequestSchema,
  askResponseSchema,
  chatHistoryResponseSchema,
  explainCriterionRequestSchema,
  explainCriterionResponseSchema,
  cvRankingItemSchema,
  compareRequestSchema,
  compareResponseSchema,
  // Types
  type ChatMessage,
  type ChatMessageRequest,
  type AskResponse,
  type ChatHistoryResponse,
  type ExplainCriterionRequest,
  type ExplainCriterionResponse,
  type CVRankingItem,
  type CompareRequest,
  type CompareResponse,
} from './chat.schemas';
