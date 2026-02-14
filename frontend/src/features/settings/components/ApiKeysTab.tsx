/**
 * @fileoverview API Keys Tab Component
 *
 * Manages user's API keys for AI providers.
 * Allows adding, validating, and deleting API keys.
 *
 * @module features/settings/components/ApiKeysTab
 */

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Input, Badge, Text } from '@/shared/components';
import { useApiKeys, useSetApiKey, useDeleteApiKey, useValidateApiKey } from '../hooks';
import type { AIProvider } from '@/shared/types';

/** Provider configuration */
const PROVIDERS: { id: AIProvider; name: string; required: boolean; placeholder: string; description: string }[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    required: true,
    placeholder: 'sk-...',
    description: 'Required for embeddings (semantic search). Also supports GPT models for evaluation.',
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    required: false,
    placeholder: 'sk-ant-...',
    description: 'Claude models - best for CV evaluation and reasoning.',
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    required: false,
    placeholder: 'AIza...',
    description: 'Fast and cost-effective models for parsing and evaluation.',
  },
];

/**
 * API Keys Tab Component
 *
 * Displays and manages API keys for all supported providers.
 *
 * @example
 * ```tsx
 * <ApiKeysTab />
 * ```
 */
export const ApiKeysTab = () => {
  const { data: apiKeysData, isLoading } = useApiKeys();
  const { mutate: setKey, isPending: isSaving } = useSetApiKey();
  const { mutate: deleteKey, isPending: isDeleting } = useDeleteApiKey();
  const { mutate: validateKey, isPending: isValidating } = useValidateApiKey();

  // Track input values and states per provider
  const [inputs, setInputs] = useState<Record<AIProvider, string>>({
    openai: '',
    anthropic: '',
    gemini: '',
  });
  const [validationResults, setValidationResults] = useState<Record<AIProvider, { valid: boolean; message: string } | null>>({
    openai: null,
    anthropic: null,
    gemini: null,
  });
  const [activeProvider, setActiveProvider] = useState<AIProvider | null>(null);

  /** Get configured key info for a provider */
  const getKeyInfo = (provider: AIProvider) => {
    return apiKeysData?.keys.find((k) => k.provider === provider);
  };

  /** Handle input change */
  const handleInputChange = (provider: AIProvider, value: string) => {
    setInputs((prev) => ({ ...prev, [provider]: value }));
    // Clear validation when input changes
    setValidationResults((prev) => ({ ...prev, [provider]: null }));
  };

  /** Validate a key before saving */
  const handleValidate = (provider: AIProvider) => {
    const apiKey = inputs[provider];
    if (!apiKey || apiKey.length < 10) return;

    setActiveProvider(provider);
    validateKey(
      { provider, apiKey },
      {
        onSuccess: (result) => {
          setValidationResults((prev) => ({
            ...prev,
            [provider]: { valid: result.is_valid, message: result.message },
          }));
          setActiveProvider(null);
        },
        onError: (error) => {
          setValidationResults((prev) => ({
            ...prev,
            [provider]: { valid: false, message: error instanceof Error ? error.message : 'Validation failed' },
          }));
          setActiveProvider(null);
        },
      }
    );
  };

  /** Save an API key */
  const handleSave = (provider: AIProvider) => {
    const apiKey = inputs[provider];
    if (!apiKey || apiKey.length < 10) return;

    setActiveProvider(provider);
    setKey(
      { provider, apiKey },
      {
        onSuccess: (result) => {
          setInputs((prev) => ({ ...prev, [provider]: '' }));
          setValidationResults((prev) => ({
            ...prev,
            [provider]: { valid: result.is_valid, message: result.message },
          }));
          setActiveProvider(null);
        },
        onError: (error) => {
          setValidationResults((prev) => ({
            ...prev,
            [provider]: { valid: false, message: error instanceof Error ? error.message : 'Save failed' },
          }));
          setActiveProvider(null);
        },
      }
    );
  };

  /** Delete an API key */
  const handleDelete = (provider: AIProvider) => {
    if (!confirm(`Are you sure you want to delete your ${provider.toUpperCase()} API key?`)) return;

    setActiveProvider(provider);
    deleteKey(provider, {
      onSuccess: () => {
        setValidationResults((prev) => ({ ...prev, [provider]: null }));
        setActiveProvider(null);
      },
      onError: () => {
        setActiveProvider(null);
      },
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Warning if OpenAI not configured */}
      {!apiKeysData?.openai_configured && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
          <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <Text weight="medium" className="text-amber-800">OpenAI API Key Required</Text>
            <Text size="sm" className="text-amber-700 mt-1">
              You need to configure an OpenAI API key to upload and analyze CVs. 
              OpenAI is required for generating embeddings (semantic search).
            </Text>
          </div>
        </div>
      )}

      {/* Provider Cards */}
      {PROVIDERS.map((provider) => {
        const keyInfo = getKeyInfo(provider.id);
        const validation = validationResults[provider.id];
        const isActive = activeProvider === provider.id;
        const inputValue = inputs[provider.id];

        return (
          <Card key={provider.id} padding="md">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CardTitle className="text-lg">{provider.name}</CardTitle>
                  {provider.required && (
                    <Badge variant="warning" size="sm">Required</Badge>
                  )}
                  {keyInfo && (
                    <Badge variant={keyInfo.is_valid ? 'success' : 'error'} size="sm">
                      {keyInfo.is_valid ? 'Configured' : 'Invalid'}
                    </Badge>
                  )}
                </div>
                {keyInfo && (
                  <Text size="sm" color="muted" className="font-mono">
                    ••••••••{keyInfo.key_hint}
                  </Text>
                )}
              </div>
              <CardDescription>{provider.description}</CardDescription>
            </CardHeader>

            <CardContent>
              <div className="space-y-4">
                {/* Input Row */}
                <div className="flex gap-3">
                  <div className="flex-1">
                    <Input
                      type="password"
                      placeholder={keyInfo ? 'Enter new key to replace...' : provider.placeholder}
                      value={inputValue}
                      onChange={(e) => handleInputChange(provider.id, e.target.value)}
                      disabled={isActive || isSaving || isDeleting}
                    />
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => handleValidate(provider.id)}
                    disabled={!inputValue || inputValue.length < 10 || isActive || isValidating}
                    isLoading={isActive && isValidating}
                  >
                    Test
                  </Button>
                  <Button
                    variant="primary"
                    onClick={() => handleSave(provider.id)}
                    disabled={!inputValue || inputValue.length < 10 || isActive || isSaving}
                    isLoading={isActive && isSaving}
                  >
                    Save
                  </Button>
                </div>

                {/* Validation Result */}
                {validation && (
                  <div className={`flex items-center gap-2 text-sm ${validation.valid ? 'text-green-600' : 'text-red-600'}`}>
                    {validation.valid ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                    <span>{validation.message}</span>
                  </div>
                )}

                {/* Delete Button (only if key exists) */}
                {keyInfo && (
                  <div className="flex justify-end pt-2 border-t border-gray-100">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(provider.id)}
                      disabled={isActive || isDeleting}
                      isLoading={isActive && isDeleting}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      Delete Key
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        );
      })}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <Text weight="medium" className="text-blue-800">Your Keys Are Secure</Text>
            <Text size="sm" className="text-blue-700 mt-1">
              API keys are encrypted with AES-256 before storage and are never exposed in API responses.
              Only the last 4 characters are shown for identification.
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
};
