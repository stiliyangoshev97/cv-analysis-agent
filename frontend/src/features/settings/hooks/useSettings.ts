/**
 * @fileoverview Settings hooks for React Query.
 *
 * Provides hooks for managing user settings:
 * - API key management
 * - Agent configuration
 * - Setup status
 *
 * @module features/settings/hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getApiKeys,
  setApiKey,
  deleteApiKey,
  validateApiKey,
  getAgentConfig,
  updateAgentConfig,
  getAvailableModels,
  getSetupStatus,
} from '../api';
import type { AIProvider, UpdateAgentConfigRequest } from '@/shared/types';

// =============================================================================
// Query Keys
// =============================================================================

/** Query keys for settings */
export const settingsKeys = {
  all: ['settings'] as const,
  apiKeys: () => [...settingsKeys.all, 'api-keys'] as const,
  agentConfig: () => [...settingsKeys.all, 'agent-config'] as const,
  availableModels: () => [...settingsKeys.all, 'available-models'] as const,
  setupStatus: () => [...settingsKeys.all, 'setup-status'] as const,
};

// =============================================================================
// API Key Hooks
// =============================================================================

/**
 * Hook to fetch user's API keys.
 *
 * @returns Query result with API key list
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useApiKeys();
 * if (data?.openai_configured) {
 *   // OpenAI is ready
 * }
 * ```
 */
export const useApiKeys = () => {
  return useQuery({
    queryKey: settingsKeys.apiKeys(),
    queryFn: getApiKeys,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

/**
 * Hook to set/update an API key.
 *
 * @returns Mutation for setting API keys
 *
 * @example
 * ```tsx
 * const { mutate: setKey, isPending } = useSetApiKey();
 * setKey({ provider: 'openai', apiKey: 'sk-...' });
 * ```
 */
export const useSetApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ provider, apiKey }: { provider: AIProvider; apiKey: string }) =>
      setApiKey(provider, apiKey),
    onSuccess: () => {
      // Invalidate both API keys and setup status
      queryClient.invalidateQueries({ queryKey: settingsKeys.apiKeys() });
      queryClient.invalidateQueries({ queryKey: settingsKeys.setupStatus() });
    },
  });
};

/**
 * Hook to delete an API key.
 *
 * @returns Mutation for deleting API keys
 *
 * @example
 * ```tsx
 * const { mutate: deleteKey } = useDeleteApiKey();
 * deleteKey('anthropic');
 * ```
 */
export const useDeleteApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (provider: AIProvider) => deleteApiKey(provider),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: settingsKeys.apiKeys() });
      queryClient.invalidateQueries({ queryKey: settingsKeys.setupStatus() });
    },
  });
};

/**
 * Hook to validate an API key without storing.
 *
 * @returns Mutation for validating API keys
 *
 * @example
 * ```tsx
 * const { mutate: validate, data } = useValidateApiKey();
 * validate({ provider: 'openai', apiKey: 'sk-...' });
 * ```
 */
export const useValidateApiKey = () => {
  return useMutation({
    mutationFn: ({ provider, apiKey }: { provider: AIProvider; apiKey: string }) =>
      validateApiKey(provider, apiKey),
  });
};

// =============================================================================
// Agent Config Hooks
// =============================================================================

/**
 * Hook to fetch agent configuration.
 *
 * @returns Query result with agent config
 *
 * @example
 * ```tsx
 * const { data: config } = useAgentConfig();
 * console.log(config?.default_llm_provider);
 * ```
 */
export const useAgentConfig = () => {
  return useQuery({
    queryKey: settingsKeys.agentConfig(),
    queryFn: getAgentConfig,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

/**
 * Hook to update agent configuration.
 *
 * @returns Mutation for updating config
 *
 * @example
 * ```tsx
 * const { mutate: updateConfig } = useUpdateAgentConfig();
 * updateConfig({ default_llm_provider: 'anthropic' });
 * ```
 */
export const useUpdateAgentConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateAgentConfigRequest) => updateAgentConfig(data),
    onSuccess: (data) => {
      queryClient.setQueryData(settingsKeys.agentConfig(), data);
    },
  });
};

// =============================================================================
// Available Models Hook
// =============================================================================

/**
 * Hook to fetch available LLM models.
 *
 * @returns Query result with available models
 *
 * @example
 * ```tsx
 * const { data: models } = useAvailableModels();
 * models?.providers.forEach(p => console.log(p.models));
 * ```
 */
export const useAvailableModels = () => {
  return useQuery({
    queryKey: settingsKeys.availableModels(),
    queryFn: getAvailableModels,
    staleTime: 1000 * 60 * 60, // 1 hour (models don't change often)
  });
};

// =============================================================================
// Setup Status Hook
// =============================================================================

/**
 * Hook to check if user has completed required setup.
 *
 * @returns Query result with setup status
 *
 * @example
 * ```tsx
 * const { data: status } = useSetupStatus();
 * if (!status?.is_complete) {
 *   // Show setup warning
 * }
 * ```
 */
export const useSetupStatus = () => {
  return useQuery({
    queryKey: settingsKeys.setupStatus(),
    queryFn: getSetupStatus,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};
