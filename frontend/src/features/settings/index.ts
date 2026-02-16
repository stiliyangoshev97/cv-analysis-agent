/**
 * @fileoverview Settings feature module.
 *
 * Provides user settings management including:
 * - API key configuration for AI providers
 * - LLM preferences (default provider, per-agent overrides)
 * - Setup status checking
 *
 * @module features/settings
 *
 * @example
 * ```tsx
 * import { SettingsPage, useSetupStatus } from '@/features/settings';
 *
 * // Check if user has completed setup
 * const { data: status } = useSetupStatus();
 * if (!status?.is_complete) {
 *   // Redirect to settings
 * }
 * ```
 */

// Pages
export { SettingsPage, LlmFaqPage } from './pages';

// Components
export { ApiKeysTab, LlmPreferencesTab, SetupBanner, SetupRequiredScreen } from './components';

// Hooks
export {
  useApiKeys,
  useSetApiKey,
  useDeleteApiKey,
  useValidateApiKey,
  useAgentConfig,
  useUpdateAgentConfig,
  useAvailableModels,
  useSetupStatus,
  settingsKeys,
} from './hooks';

// API functions
export {
  getApiKeys,
  setApiKey,
  deleteApiKey,
  validateApiKey,
  getAgentConfig,
  updateAgentConfig,
  getAvailableModels,
  getSetupStatus,
} from './api';
