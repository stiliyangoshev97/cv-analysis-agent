/**
 * @fileoverview Settings-related Zod schemas.
 *
 * Defines validation schemas for user settings including API keys
 * and LLM provider configuration.
 *
 * @module schemas/settings
 */

import { z } from 'zod';

// =============================================================================
// API Key Schemas
// =============================================================================

/** AI Provider types */
export const aiProviderSchema = z.enum(['openai', 'anthropic', 'gemini']);
export type AIProvider = z.infer<typeof aiProviderSchema>;

/** LLM Provider types (subset used for chat/evaluation) */
export const llmProviderSchema = z.enum(['anthropic', 'openai', 'gemini']);
export type LLMProvider = z.infer<typeof llmProviderSchema>;

/**
 * Schema for API key information (without exposing actual key).
 */
export const apiKeyInfoSchema = z.object({
  provider: z.string(),
  key_hint: z.string(),
  is_valid: z.boolean(),
  is_required: z.boolean().default(false),
});
export type ApiKeyInfo = z.infer<typeof apiKeyInfoSchema>;

/**
 * Schema for list of API keys response.
 */
export const apiKeyListResponseSchema = z.object({
  keys: z.array(apiKeyInfoSchema),
  openai_configured: z.boolean(),
});
export type ApiKeyListResponse = z.infer<typeof apiKeyListResponseSchema>;

/**
 * Schema for setting an API key request.
 */
export const setApiKeyRequestSchema = z.object({
  api_key: z.string().min(10, 'API key must be at least 10 characters'),
});
export type SetApiKeyRequest = z.infer<typeof setApiKeyRequestSchema>;

/**
 * Schema for set API key response.
 */
export const setApiKeyResponseSchema = z.object({
  provider: z.string(),
  key_hint: z.string(),
  is_valid: z.boolean(),
  message: z.string(),
});
export type SetApiKeyResponse = z.infer<typeof setApiKeyResponseSchema>;

/**
 * Schema for validating an API key request.
 */
export const validateKeyRequestSchema = z.object({
  provider: aiProviderSchema,
  api_key: z.string().min(10, 'API key must be at least 10 characters'),
});
export type ValidateKeyRequest = z.infer<typeof validateKeyRequestSchema>;

/**
 * Schema for validate key response.
 */
export const validateKeyResponseSchema = z.object({
  provider: z.string(),
  is_valid: z.boolean(),
  message: z.string(),
});
export type ValidateKeyResponse = z.infer<typeof validateKeyResponseSchema>;

// =============================================================================
// Agent Config Schemas
// =============================================================================

/**
 * Schema for agent configuration response.
 */
export const agentConfigResponseSchema = z.object({
  default_llm_provider: llmProviderSchema.nullable().default('anthropic'),
  default_llm_model: z.string().nullable().default(null),
  chat_provider: llmProviderSchema.nullable().default(null),
  chat_model: z.string().nullable().default(null),
  scorer_provider: llmProviderSchema.nullable().default(null),
  scorer_model: z.string().nullable().default(null),
  // Read-only (always OpenAI)
  embeddings_provider: z.string().default('openai'),
  embeddings_model: z.string().default('text-embedding-3-small'),
});
export type AgentConfigResponse = z.infer<typeof agentConfigResponseSchema>;

/**
 * Schema for updating agent configuration.
 */
export const updateAgentConfigRequestSchema = z.object({
  default_llm_provider: llmProviderSchema.nullable().optional(),
  default_llm_model: z.string().nullable().optional(),
  chat_provider: llmProviderSchema.nullable().optional(),
  chat_model: z.string().nullable().optional(),
  scorer_provider: llmProviderSchema.nullable().optional(),
  scorer_model: z.string().nullable().optional(),
});
export type UpdateAgentConfigRequest = z.infer<typeof updateAgentConfigRequestSchema>;

// =============================================================================
// Available Models Schemas
// =============================================================================

/**
 * Schema for a model option.
 */
export const modelOptionSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
});
export type ModelOption = z.infer<typeof modelOptionSchema>;

/**
 * Schema for provider models.
 */
export const providerModelsSchema = z.object({
  provider: z.string(),
  provider_name: z.string(),
  models: z.array(modelOptionSchema),
});
export type ProviderModels = z.infer<typeof providerModelsSchema>;

/**
 * Schema for available models response.
 */
export const availableModelsResponseSchema = z.object({
  providers: z.array(providerModelsSchema),
});
export type AvailableModelsResponse = z.infer<typeof availableModelsResponseSchema>;

// =============================================================================
// Setup Status Schema
// =============================================================================

/**
 * Schema for setup status response.
 */
export const setupStatusResponseSchema = z.object({
  is_complete: z.boolean(),
  openai_configured: z.boolean(),
  llm_configured: z.boolean(),
  missing: z.array(z.string()),
});
export type SetupStatusResponse = z.infer<typeof setupStatusResponseSchema>;
