/**
 * @fileoverview Settings API functions.
 *
 * Provides functions for all settings-related API calls:
 * - API key management (list, set, delete, validate)
 * - Agent configuration (get, update)
 * - Available models listing
 * - Setup status check
 *
 * @module features/settings/api
 */

import { apiClient } from '@/shared/api';
import type {
  AIProvider,
  ApiKeyListResponse,
  SetApiKeyRequest,
  SetApiKeyResponse,
  ValidateKeyRequest,
  ValidateKeyResponse,
  AgentConfigResponse,
  UpdateAgentConfigRequest,
  AvailableModelsResponse,
  SetupStatusResponse,
} from '@/shared/types';

// =============================================================================
// API Key Management
// =============================================================================

/**
 * Get all configured API keys for the current user.
 * Returns key hints only, not actual keys.
 *
 * @returns Promise resolving to list of API key info
 *
 * @example
 * ```typescript
 * const { keys, openai_configured } = await getApiKeys();
 * ```
 */
export const getApiKeys = async (): Promise<ApiKeyListResponse> => {
  const response = await apiClient.get<ApiKeyListResponse>('/api/settings/api-keys');
  return response.data;
};

/**
 * Set or update an API key for a provider.
 * The key is validated and encrypted before storage.
 *
 * @param provider - AI provider (openai, anthropic, gemini)
 * @param apiKey - The API key to store
 * @returns Promise resolving to set key response
 *
 * @example
 * ```typescript
 * const result = await setApiKey('openai', 'sk-...');
 * if (result.is_valid) {
 *   console.log('Key saved!');
 * }
 * ```
 */
export const setApiKey = async (
  provider: AIProvider,
  apiKey: string
): Promise<SetApiKeyResponse> => {
  const body: SetApiKeyRequest = { api_key: apiKey };
  const response = await apiClient.put<SetApiKeyResponse>(
    `/api/settings/api-keys/${provider}`,
    body
  );
  return response.data;
};

/**
 * Delete an API key for a provider.
 *
 * @param provider - AI provider to delete key for
 * @returns Promise resolving to deletion confirmation
 *
 * @example
 * ```typescript
 * await deleteApiKey('anthropic');
 * ```
 */
export const deleteApiKey = async (provider: AIProvider): Promise<{ message: string }> => {
  const response = await apiClient.delete<{ message: string }>(
    `/api/settings/api-keys/${provider}`
  );
  return response.data;
};

/**
 * Validate an API key without storing it.
 * Makes a test API call to verify the key works.
 *
 * @param provider - AI provider to validate against
 * @param apiKey - The API key to validate
 * @returns Promise resolving to validation result
 *
 * @example
 * ```typescript
 * const result = await validateApiKey('openai', 'sk-...');
 * if (result.is_valid) {
 *   // Key is valid, can proceed to save
 * }
 * ```
 */
export const validateApiKey = async (
  provider: AIProvider,
  apiKey: string
): Promise<ValidateKeyResponse> => {
  const body: ValidateKeyRequest = { provider, api_key: apiKey };
  const response = await apiClient.post<ValidateKeyResponse>(
    '/api/settings/validate-key',
    body
  );
  return response.data;
};

// =============================================================================
// Agent Configuration
// =============================================================================

/**
 * Get current agent configuration (LLM preferences).
 *
 * @returns Promise resolving to agent config
 *
 * @example
 * ```typescript
 * const config = await getAgentConfig();
 * console.log(`Default LLM: ${config.default_llm_provider}`);
 * ```
 */
export const getAgentConfig = async (): Promise<AgentConfigResponse> => {
  const response = await apiClient.get<AgentConfigResponse>('/api/settings/agent-config');
  return response.data;
};

/**
 * Update agent configuration.
 *
 * @param data - Configuration values to update
 * @returns Promise resolving to updated config
 *
 * @example
 * ```typescript
 * const updated = await updateAgentConfig({
 *   default_llm_provider: 'anthropic',
 *   default_llm_model: 'claude-sonnet-4-20250514'
 * });
 * ```
 */
export const updateAgentConfig = async (
  data: UpdateAgentConfigRequest
): Promise<AgentConfigResponse> => {
  const response = await apiClient.put<AgentConfigResponse>(
    '/api/settings/agent-config',
    data
  );
  return response.data;
};

// =============================================================================
// Available Models
// =============================================================================

/**
 * Get list of available LLM providers and their models.
 *
 * @returns Promise resolving to available models
 *
 * @example
 * ```typescript
 * const { providers } = await getAvailableModels();
 * providers.forEach(p => console.log(p.provider_name, p.models));
 * ```
 */
export const getAvailableModels = async (): Promise<AvailableModelsResponse> => {
  const response = await apiClient.get<AvailableModelsResponse>(
    '/api/settings/available-models'
  );
  return response.data;
};

// =============================================================================
// Setup Status
// =============================================================================

/**
 * Check if user has completed required setup.
 * OpenAI key is required for embeddings.
 *
 * @returns Promise resolving to setup status
 *
 * @example
 * ```typescript
 * const status = await getSetupStatus();
 * if (!status.is_complete) {
 *   // Redirect to settings
 * }
 * ```
 */
export const getSetupStatus = async (): Promise<SetupStatusResponse> => {
  const response = await apiClient.get<SetupStatusResponse>('/api/settings/setup-status');
  return response.data;
};
