/**
 * @fileoverview Setup Banner Component
 *
 * Persistent warning banner shown when user setup is incomplete.
 * Displays until OpenAI API key is configured.
 *
 * @module features/settings/components/SetupBanner
 */

import { Link } from 'react-router-dom';
import { useSetupStatus } from '../hooks';

/**
 * Setup Banner Component
 *
 * Shows a persistent warning banner when setup is incomplete.
 * Links to settings page for configuration.
 *
 * @example
 * ```tsx
 * // In RootLayout
 * <SetupBanner />
 * ```
 */
export const SetupBanner = () => {
  const { data: status, isLoading } = useSetupStatus();

  // Don't show while loading or if setup is complete
  if (isLoading || !status || status.is_complete) {
    return null;
  }

  return (
    <div className="bg-amber-500 text-white px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <svg
            className="w-5 h-5 flex-shrink-0"
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
          <div>
            <span className="font-medium">Setup Required: </span>
            <span>
              {!status.openai_configured
                ? 'Configure your OpenAI API key to enable CV analysis.'
                : 'Configure at least one LLM provider to evaluate CVs.'}
            </span>
          </div>
        </div>
        <Link
          to="/settings"
          className="flex-shrink-0 bg-white text-amber-600 px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-amber-50 transition-colors"
        >
          Go to Settings
        </Link>
      </div>
    </div>
  );
};
