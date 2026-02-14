/**
 * @fileoverview LLM Preferences Tab Component
 *
 * Manages user's LLM provider preferences for different agents.
 * Allows selecting default provider and per-agent overrides.
 *
 * @module features/settings/components/LlmPreferencesTab
 */

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Select, Text, Badge } from '@/shared/components';
import { useAgentConfig, useUpdateAgentConfig, useAvailableModels, useApiKeys } from '../hooks';
import type { LLMProvider } from '@/shared/types';

/**
 * LLM Preferences Tab Component
 *
 * Configures default LLM provider and per-agent overrides.
 *
 * @example
 * ```tsx
 * <LlmPreferencesTab />
 * ```
 */
export const LlmPreferencesTab = () => {
  const { data: config, isLoading: isLoadingConfig } = useAgentConfig();
  const { data: modelsData, isLoading: isLoadingModels } = useAvailableModels();
  const { data: apiKeysData } = useApiKeys();
  const { mutate: updateConfig, isPending: isSaving } = useUpdateAgentConfig();

  // Local state for form
  const [defaultProvider, setDefaultProvider] = useState<LLMProvider | null>(null);
  const [defaultModel, setDefaultModel] = useState<string | null>(null);
  const [chatProvider, setChatProvider] = useState<LLMProvider | null>(null);
  const [chatModel, setChatModel] = useState<string | null>(null);
  const [scorerProvider, setScorerProvider] = useState<LLMProvider | null>(null);
  const [scorerModel, setScorerModel] = useState<string | null>(null);

  // Sync from server config
  useEffect(() => {
    if (config) {
      setDefaultProvider(config.default_llm_provider);
      setDefaultModel(config.default_llm_model);
      setChatProvider(config.chat_provider);
      setChatModel(config.chat_model);
      setScorerProvider(config.scorer_provider);
      setScorerModel(config.scorer_model);
    }
  }, [config]);

  /** Check if a provider is configured */
  const isProviderConfigured = (provider: LLMProvider): boolean => {
    if (!apiKeysData) return false;
    return apiKeysData.keys.some((k) => k.provider === provider && k.is_valid);
  };

  /** Get models for a specific provider */
  const getModelsForProvider = (provider: LLMProvider | null) => {
    if (!provider || !modelsData) return [];
    const providerData = modelsData.providers.find((p) => p.provider === provider);
    return providerData?.models || [];
  };

  /** Provider options for select */
  const providerOptions = [
    { value: '', label: 'Use Default' },
    { value: 'anthropic', label: 'Anthropic Claude' },
    { value: 'openai', label: 'OpenAI GPT' },
    { value: 'gemini', label: 'Google Gemini' },
  ];

  /** Default provider options (no "Use Default") */
  const defaultProviderOptions = [
    { value: 'anthropic', label: 'Anthropic Claude' },
    { value: 'openai', label: 'OpenAI GPT' },
    { value: 'gemini', label: 'Google Gemini' },
  ];

  /** Handle save */
  const handleSave = () => {
    updateConfig({
      default_llm_provider: defaultProvider,
      default_llm_model: defaultModel,
      chat_provider: chatProvider,
      chat_model: chatModel,
      scorer_provider: scorerProvider,
      scorer_model: scorerModel,
    });
  };

  /** Check if form has changes */
  const hasChanges = config && (
    defaultProvider !== config.default_llm_provider ||
    defaultModel !== config.default_llm_model ||
    chatProvider !== config.chat_provider ||
    chatModel !== config.chat_model ||
    scorerProvider !== config.scorer_provider ||
    scorerModel !== config.scorer_model
  );

  if (isLoadingConfig || isLoadingModels) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Get effective providers (what will actually be used)
  const effectiveChatProvider = chatProvider || defaultProvider;
  const effectiveScorerProvider = scorerProvider || defaultProvider;

  return (
    <div className="space-y-6">
      {/* Default LLM Provider */}
      <Card padding="md">
        <CardHeader>
          <CardTitle className="text-lg">Default LLM Provider</CardTitle>
          <CardDescription>
            Choose your preferred AI provider for all agents. Individual agents can override this below.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Select
                label="Provider"
                options={defaultProviderOptions}
                value={defaultProvider || 'anthropic'}
                onChange={(e) => {
                  const provider = e.target.value as LLMProvider;
                  setDefaultProvider(provider);
                  setDefaultModel(null); // Reset model when provider changes
                }}
              />
              {defaultProvider && !isProviderConfigured(defaultProvider) && (
                <Text size="sm" className="text-amber-600 mt-1">
                  ⚠️ API key not configured for this provider
                </Text>
              )}
            </div>
            <div>
              <Select
                label="Model"
                options={[
                  { value: '', label: 'Auto (recommended)' },
                  ...getModelsForProvider(defaultProvider).map((m) => ({
                    value: m.id,
                    label: m.name,
                  })),
                ]}
                value={defaultModel || ''}
                onChange={(e) => setDefaultModel(e.target.value || null)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Per-Agent Overrides */}
      <Card padding="md">
        <CardHeader>
          <CardTitle className="text-lg">Per-Agent Overrides</CardTitle>
          <CardDescription>
            Optionally use different providers for specific agents. Leave as "Use Default" to inherit from above.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Chat Agent */}
            <div className="pb-6 border-b border-gray-100">
              <div className="flex items-center gap-2 mb-3">
                <Text weight="medium">Chat Agent</Text>
                <Badge variant="info" size="sm">RAG Q&A</Badge>
              </div>
              <Text size="sm" color="muted" className="mb-4">
                Answers questions about CVs and explains evaluation scores.
              </Text>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Select
                    label="Provider"
                    options={providerOptions}
                    value={chatProvider || ''}
                    onChange={(e) => {
                      const provider = e.target.value as LLMProvider | '';
                      setChatProvider(provider || null);
                      setChatModel(null);
                    }}
                  />
                  {chatProvider && !isProviderConfigured(chatProvider) && (
                    <Text size="sm" className="text-amber-600 mt-1">
                      ⚠️ API key not configured
                    </Text>
                  )}
                </div>
                <div>
                  <Select
                    label="Model"
                    options={[
                      { value: '', label: chatProvider ? 'Auto' : 'Use Default Model' },
                      ...getModelsForProvider(chatProvider || defaultProvider).map((m) => ({
                        value: m.id,
                        label: m.name,
                      })),
                    ]}
                    value={chatModel || ''}
                    onChange={(e) => setChatModel(e.target.value || null)}
                    disabled={!chatProvider}
                  />
                </div>
              </div>
              {effectiveChatProvider && (
                <Text size="sm" color="muted" className="mt-2">
                  Will use: <span className="font-medium">{effectiveChatProvider}</span>
                </Text>
              )}
            </div>

            {/* Scorer Agent */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Text weight="medium">Scorer Agent</Text>
                <Badge variant="success" size="sm">CV Evaluation</Badge>
              </div>
              <Text size="sm" color="muted" className="mb-4">
                Evaluates CVs against criteria and generates scores with reasoning.
              </Text>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Select
                    label="Provider"
                    options={providerOptions}
                    value={scorerProvider || ''}
                    onChange={(e) => {
                      const provider = e.target.value as LLMProvider | '';
                      setScorerProvider(provider || null);
                      setScorerModel(null);
                    }}
                  />
                  {scorerProvider && !isProviderConfigured(scorerProvider) && (
                    <Text size="sm" className="text-amber-600 mt-1">
                      ⚠️ API key not configured
                    </Text>
                  )}
                </div>
                <div>
                  <Select
                    label="Model"
                    options={[
                      { value: '', label: scorerProvider ? 'Auto' : 'Use Default Model' },
                      ...getModelsForProvider(scorerProvider || defaultProvider).map((m) => ({
                        value: m.id,
                        label: m.name,
                      })),
                    ]}
                    value={scorerModel || ''}
                    onChange={(e) => setScorerModel(e.target.value || null)}
                    disabled={!scorerProvider}
                  />
                </div>
              </div>
              {effectiveScorerProvider && (
                <Text size="sm" color="muted" className="mt-2">
                  Will use: <span className="font-medium">{effectiveScorerProvider}</span>
                </Text>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Embeddings (Read-only) */}
      <Card padding="md" className="bg-gray-50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg">Embeddings</CardTitle>
            <Badge variant="neutral" size="sm">Fixed</Badge>
          </div>
          <CardDescription>
            Embeddings are always generated using OpenAI for consistency in semantic search.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Text size="sm" weight="medium" className="mb-1">Provider</Text>
              <div className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-gray-600">
                OpenAI
              </div>
            </div>
            <div>
              <Text size="sm" weight="medium" className="mb-1">Model</Text>
              <div className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-gray-600">
                text-embedding-3-small
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={!hasChanges || isSaving}
          isLoading={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Preferences'}
        </Button>
      </div>
    </div>
  );
};
