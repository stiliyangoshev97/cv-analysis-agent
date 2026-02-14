/**
 * @fileoverview Settings Page Component
 *
 * Main settings page with tabs for API Keys and LLM Preferences.
 * Required for CV uploads to work (OpenAI key must be configured).
 *
 * @module features/settings/pages/SettingsPage
 */

import { useState, type ReactNode } from 'react';
import { Container, Card, Heading, Text, Badge } from '@/shared/components';
import { ApiKeysTab } from '../components/ApiKeysTab';
import { LlmPreferencesTab } from '../components/LlmPreferencesTab';
import { useSetupStatus } from '../hooks';

/** Tab type */
type SettingsTab = 'api-keys' | 'llm-preferences';

/**
 * Settings Page Component
 *
 * Two-tab interface for managing API keys and LLM preferences.
 *
 * @example
 * ```tsx
 * <SettingsPage />
 * ```
 */
export const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('api-keys');
  const { data: setupStatus } = useSetupStatus();

  const tabs: { id: SettingsTab; label: string; icon: ReactNode }[] = [
    {
      id: 'api-keys',
      label: 'API Keys',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
        </svg>
      ),
    },
    {
      id: 'llm-preferences',
      label: 'LLM Preferences',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
    },
  ];

  return (
    <Container size="lg" className="py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Heading level={1}>Settings</Heading>
          {setupStatus && !setupStatus.is_complete && (
            <Badge variant="warning">Setup Required</Badge>
          )}
        </div>
        <Text color="muted">
          Configure your AI providers and preferences. OpenAI API key is required for CV analysis.
        </Text>
      </div>

      {/* Setup Status Warning */}
      {setupStatus && !setupStatus.is_complete && (
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <Text weight="medium" className="text-amber-800">
                Complete Setup to Upload CVs
              </Text>
              <Text size="sm" className="text-amber-700 mt-1">
                Missing: {setupStatus.missing?.join(', ') || 'Required configuration'}
              </Text>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <Card padding="none">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'api-keys' && <ApiKeysTab />}
          {activeTab === 'llm-preferences' && <LlmPreferencesTab />}
        </div>
      </Card>
    </Container>
  );
};
