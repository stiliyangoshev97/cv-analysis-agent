/**
 * @fileoverview Setup Required Screen Component
 *
 * Full-page blocker shown when trying to access features
 * that require setup (like CV upload) before configuration is complete.
 *
 * @module features/settings/components/SetupRequiredScreen
 */

import { Link } from 'react-router-dom';
import { Container, Card, CardContent, Button, Heading, Text } from '@/shared/components';
import { useSetupStatus } from '../hooks';

/**
 * Setup Required Screen Component
 *
 * Blocks access to features until setup is complete.
 * Shows what's missing and links to settings.
 *
 * @example
 * ```tsx
 * const { data: status } = useSetupStatus();
 * if (!status?.is_complete) {
 *   return <SetupRequiredScreen />;
 * }
 * ```
 */
export const SetupRequiredScreen = () => {
  const { data: status } = useSetupStatus();

  const missingItems = status?.missing || ['OpenAI API Key'];

  return (
    <Container size="sm" className="py-16">
      <Card padding="lg" className="text-center">
        <CardContent>
          {/* Icon */}
          <div className="mx-auto w-16 h-16 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center mb-6">
            <svg
              className="w-8 h-8 text-amber-600 dark:text-amber-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>

          {/* Title */}
          <Heading level={2} className="mb-3">
            Setup Required
          </Heading>

          {/* Description */}
          <Text color="muted" className="mb-6 max-w-md mx-auto">
            Before you can upload and analyze CVs, you need to configure your API keys.
            This only takes a minute!
          </Text>

          {/* Missing Items */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
            <Text size="sm" weight="medium" className="mb-3 text-gray-700 dark:text-gray-300">
              Missing Configuration:
            </Text>
            <ul className="space-y-2">
              {missingItems.map((item, index) => (
                <li
                  key={index}
                  className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"
                >
                  <svg
                    className="w-4 h-4 text-amber-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* Why Required */}
          <div className="text-left bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-6">
            <Text size="sm" weight="medium" className="text-blue-800 dark:text-blue-200 mb-2">
              Why is this required?
            </Text>
            <ul className="space-y-1 text-sm text-blue-700 dark:text-blue-300">
              <li>
                • <strong>OpenAI API Key</strong>: Required for generating embeddings
                (semantic search across CVs)
              </li>
              <li>
                • <strong>LLM Provider</strong>: Required for AI-powered CV evaluation
                (Claude, GPT, or Gemini)
              </li>
            </ul>
          </div>

          {/* CTA Button */}
          <Link to="/settings" className="inline-block">
            <Button size="lg" className="w-full sm:w-auto">
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                Go to Settings
              </span>
            </Button>
          </Link>
        </CardContent>
      </Card>
    </Container>
  );
};
