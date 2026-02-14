/**
 * @fileoverview Template Selector Component.
 *
 * Dropdown for selecting an evaluation profile/template before CV upload.
 *
 * @module features/cv/components/TemplateSelector
 */

import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Text, Spinner, Badge } from '@/shared/components/ui';
import { useProfiles } from '@/features/profile';
import type { ProfileSummary } from '@/shared/schemas';

/** LocalStorage key for persisting selected template */
const SELECTED_TEMPLATE_KEY = 'cv-screening-selected-template';

interface TemplateSelectorProps {
  /** Currently selected template ID */
  selectedId: string | null;
  /** Called when selection changes */
  onSelect: (template: ProfileSummary | null) => void;
  /** Whether selector is disabled */
  disabled?: boolean;
}

/**
 * Template Selector
 *
 * Allows users to select an evaluation profile before uploading CVs.
 * Persists selection to localStorage for convenience.
 *
 * @example
 * ```tsx
 * <TemplateSelector
 *   selectedId={templateId}
 *   onSelect={(t) => setTemplateId(t?.id ?? null)}
 * />
 * ```
 */
export const TemplateSelector = ({
  selectedId,
  onSelect,
  disabled = false,
}: TemplateSelectorProps) => {
  const { data, isLoading, error } = useProfiles();

  // Load saved selection from localStorage on mount
  useEffect(() => {
    if (!selectedId && data?.profiles.length) {
      const savedId = localStorage.getItem(SELECTED_TEMPLATE_KEY);
      if (savedId) {
        const savedTemplate = data.profiles.find((p) => p.id === savedId);
        if (savedTemplate) {
          onSelect(savedTemplate);
        }
      }
    }
  }, [data, selectedId, onSelect]);

  // Save selection to localStorage
  const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    if (!id) {
      localStorage.removeItem(SELECTED_TEMPLATE_KEY);
      onSelect(null);
    } else {
      localStorage.setItem(SELECTED_TEMPLATE_KEY, id);
      const template = data?.profiles.find((p) => p.id === id);
      onSelect(template ?? null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <Spinner size="sm" />
        <Text size="sm" color="muted">Loading templates...</Text>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
        <Text size="sm" variant="error">Failed to load evaluation templates</Text>
      </div>
    );
  }

  const profiles = data?.profiles ?? [];
  const selectedProfile = profiles.find((p) => p.id === selectedId);

  return (
    <div className="space-y-3">
      {/* Selector Label */}
      <div className="flex items-center justify-between">
        <label
          htmlFor="template-select"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Evaluation Template <span className="text-red-500">*</span>
        </label>
        <Link
          to="/profiles"
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          Manage Templates
        </Link>
      </div>

      {/* Dropdown */}
      <div className="relative">
        <select
          id="template-select"
          value={selectedId ?? ''}
          onChange={handleSelect}
          disabled={disabled || profiles.length === 0}
          className={`
            w-full px-4 py-3 pr-10 rounded-lg border appearance-none
            bg-white dark:bg-gray-800
            text-gray-900 dark:text-white
            border-gray-300 dark:border-gray-600
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            disabled:opacity-50 disabled:cursor-not-allowed
            ${!selectedId ? 'text-gray-500' : ''}
          `}
        >
          <option value="">Select a template...</option>
          
          {/* System Templates */}
          {profiles.filter(p => p.is_system_template).length > 0 && (
            <optgroup label="System Templates">
              {profiles
                .filter((p) => p.is_system_template)
                .map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name} ({profile.criteria_count} criteria)
                  </option>
                ))}
            </optgroup>
          )}

          {/* User Templates */}
          {profiles.filter(p => !p.is_system_template).length > 0 && (
            <optgroup label="My Templates">
              {profiles
                .filter((p) => !p.is_system_template)
                .map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name} ({profile.criteria_count} criteria)
                  </option>
                ))}
            </optgroup>
          )}
        </select>

        {/* Dropdown Arrow */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>

      {/* Selected Template Info */}
      {selectedProfile && (
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-start justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <Text size="sm" weight="medium" className="text-blue-900 dark:text-blue-100">
                  {selectedProfile.name}
                </Text>
                {selectedProfile.is_system_template && (
                  <Badge variant="info" size="sm">System</Badge>
                )}
              </div>
              {selectedProfile.description && (
                <Text size="sm" className="text-blue-700 dark:text-blue-300 mt-0.5">
                  {selectedProfile.description}
                </Text>
              )}
            </div>
            <div className="text-right">
              <Text size="sm" className="text-blue-600 dark:text-blue-400">
                {selectedProfile.criteria_count} criteria
              </Text>
              <Text size="sm" className="text-blue-600 dark:text-blue-400">
                Pass: {selectedProfile.passing_score}%
              </Text>
            </div>
          </div>
        </div>
      )}

      {/* No Templates Warning */}
      {profiles.length === 0 && (
        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
          <Text size="sm" className="text-yellow-800 dark:text-yellow-200">
            No evaluation templates found.{' '}
            <Link
              to="/profiles/new"
              className="font-medium underline hover:no-underline"
            >
              Create one
            </Link>
            {' '}to start screening CVs.
          </Text>
        </div>
      )}

      {/* Required Warning */}
      {!selectedId && profiles.length > 0 && (
        <Text size="sm" color="muted">
          You must select an evaluation template before uploading CVs.
        </Text>
      )}
    </div>
  );
};
