/**
 * @fileoverview Template Selector Component.
 *
 * Custom dropdown for selecting an evaluation profile/template before CV upload.
 * Uses a fully custom dropdown for consistent styling across browsers.
 *
 * @module features/cv/components/TemplateSelector
 */

import { useEffect, useState, useRef } from 'react';
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
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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

  // Handle template selection
  const handleSelectTemplate = (template: ProfileSummary) => {
    localStorage.setItem(SELECTED_TEMPLATE_KEY, template.id);
    onSelect(template);
    setIsOpen(false);
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
  const systemTemplates = profiles.filter((p) => p.is_system_template);
  const userTemplates = profiles.filter((p) => !p.is_system_template);

  return (
    <div className="space-y-3">
      {/* Selector Label */}
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Evaluation Template <span className="text-red-500">*</span>
        </label>
        <Link
          to="/profiles"
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          Manage Templates
        </Link>
      </div>

      {/* Custom Dropdown */}
      <div className="relative" ref={dropdownRef}>
        {/* Trigger Button */}
        <button
          type="button"
          onClick={() => !disabled && profiles.length > 0 && setIsOpen(!isOpen)}
          disabled={disabled || profiles.length === 0}
          className={`
            w-full px-4 py-3 rounded-lg border text-left flex items-center justify-between
            transition-all duration-200
            ${disabled || profiles.length === 0
              ? 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-gray-800'
              : 'bg-white dark:bg-gray-800 hover:border-blue-400 dark:hover:border-blue-500 cursor-pointer'
            }
            ${isOpen
              ? 'border-blue-500 ring-2 ring-blue-500/20'
              : 'border-gray-300 dark:border-gray-600'
            }
          `}
        >
          {selectedProfile ? (
            <div className="flex items-center gap-2 min-w-0">
              <span className="font-medium text-gray-900 dark:text-white truncate">
                {selectedProfile.name}
              </span>
              {selectedProfile.is_system_template && (
                <Badge variant="info" size="sm">System</Badge>
              )}
              <span className="text-gray-500 dark:text-gray-400 text-sm">
                ({selectedProfile.criteria_count} criteria)
              </span>
            </div>
          ) : (
            <span className="text-gray-500 dark:text-gray-400">
              Select a template...
            </span>
          )}
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform duration-200 flex-shrink-0 ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-xl overflow-hidden">
            <div className="max-h-80 overflow-y-auto">
              {/* System Templates Section */}
              {systemTemplates.length > 0 && (
                <>
                  <div className="px-3 py-2 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
                    <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      System Templates
                    </span>
                  </div>
                  {systemTemplates.map((profile) => (
                    <TemplateOption
                      key={profile.id}
                      profile={profile}
                      isSelected={selectedId === profile.id}
                      onSelect={() => handleSelectTemplate(profile)}
                    />
                  ))}
                </>
              )}

              {/* User Templates Section */}
              {userTemplates.length > 0 && (
                <>
                  <div className="px-3 py-2 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
                    <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      My Templates
                    </span>
                  </div>
                  {userTemplates.map((profile) => (
                    <TemplateOption
                      key={profile.id}
                      profile={profile}
                      isSelected={selectedId === profile.id}
                      onSelect={() => handleSelectTemplate(profile)}
                    />
                  ))}
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Selected Template Info Card */}
      {selectedProfile && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <Text size="sm" weight="medium" className="text-blue-900 dark:text-blue-100">
              {selectedProfile.name}
            </Text>
            {selectedProfile.is_system_template && (
              <Badge variant="info" size="sm">System</Badge>
            )}
          </div>
          {selectedProfile.description && (
            <Text size="sm" className="text-blue-700 dark:text-blue-300 mb-3 line-clamp-2">
              {selectedProfile.description}
            </Text>
          )}
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-100 dark:bg-blue-800/50 text-xs font-medium text-blue-700 dark:text-blue-300">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              {selectedProfile.criteria_count} {selectedProfile.criteria_count === 1 ? 'criterion' : 'criteria'}
            </span>
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
              selectedProfile.passing_score >= 70 
                ? 'bg-green-100 text-green-700 dark:bg-green-800/50 dark:text-green-300'
                : selectedProfile.passing_score >= 50
                  ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-800/50 dark:text-yellow-300'
                  : 'bg-red-100 text-red-700 dark:bg-red-800/50 dark:text-red-300'
            }`}>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {selectedProfile.passing_score}% to pass
            </span>
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

/** Individual template option in the dropdown */
const TemplateOption = ({
  profile,
  isSelected,
  onSelect,
}: {
  profile: ProfileSummary;
  isSelected: boolean;
  onSelect: () => void;
}) => {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`
        w-full px-4 py-3 text-left flex items-start gap-3 transition-colors
        hover:bg-blue-50 dark:hover:bg-blue-900/30
        ${isSelected ? 'bg-blue-50 dark:bg-blue-900/30' : ''}
        border-b border-gray-100 dark:border-gray-700/50 last:border-b-0
      `}
    >
      {/* Selection indicator */}
      <div className={`
        flex-shrink-0 w-5 h-5 rounded-full border-2 mt-0.5 flex items-center justify-center
        ${isSelected
          ? 'border-blue-600 bg-blue-600'
          : 'border-gray-300 dark:border-gray-600'
        }
      `}>
        {isSelected && (
          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        )}
      </div>

      {/* Template info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className={`font-medium truncate ${isSelected ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'}`}>
            {profile.name}
          </span>
          {profile.is_system_template && (
            <Badge variant="info" size="sm">System</Badge>
          )}
        </div>
        {profile.description && (
          <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-1 mb-1">
            {profile.description}
          </p>
        )}
        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {profile.criteria_count} criteria
          </span>
          <span className={`flex items-center gap-1 ${
            profile.passing_score >= 70 
              ? 'text-green-600 dark:text-green-400'
              : profile.passing_score >= 50
                ? 'text-yellow-600 dark:text-yellow-400'
                : 'text-red-600 dark:text-red-400'
          }`}>
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {profile.passing_score}% pass
          </span>
        </div>
      </div>
    </button>
  );
};
