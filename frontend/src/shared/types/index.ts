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
  CVSummary,
  CVListResponse,
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
  // Notification Types
  NotificationSettings,
  NotificationSettingsUpdate,
  NotificationChannel,
  SendTestNotificationRequest,
  NotificationResult,
  NotificationServiceStatus,
  // Settings Types
  AIProvider,
  LLMProvider,
  ApiKeyInfo,
  ApiKeyListResponse,
  SetApiKeyRequest,
  SetApiKeyResponse,
  ValidateKeyRequest,
  ValidateKeyResponse,
  AgentConfigResponse,
  UpdateAgentConfigRequest,
  ModelOption,
  ProviderModels,
  AvailableModelsResponse,
  SetupStatusResponse,
  // Chat Types
  ChatMessage,
  ChatMessageRequest,
  AskResponse,
  ChatHistoryResponse,
  ExplainCriterionRequest,
  ExplainCriterionResponse,
  CVRankingItem,
  CompareRequest,
  CompareResponse,
} from '../schemas';
