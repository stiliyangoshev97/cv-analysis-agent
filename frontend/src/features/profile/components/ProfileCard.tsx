/**
 * @fileoverview Profile Card Component.
 *
 * Displays a single profile summary in a card format.
 *
 * @module features/profile/components/ProfileCard
 */

import type { ProfileSummary } from '@/shared/schemas';
import { Card, Badge, Text } from '@/shared/components/ui';

interface ProfileCardProps {
  /** Profile data */
  profile: ProfileSummary;
  /** Called when card is clicked */
  onClick?: () => void;
  /** Called when edit button is clicked */
  onEdit?: () => void;
  /** Called when clone button is clicked */
  onClone?: () => void;
  /** Called when delete button is clicked */
  onDelete?: () => void;
}

/**
 * Profile Card Component
 *
 * Displays profile summary with action buttons.
 *
 * @example
 * ```tsx
 * <ProfileCard
 *   profile={profile}
 *   onClick={() => navigate(`/profiles/${profile.id}`)}
 *   onEdit={() => navigate(`/profiles/${profile.id}/edit`)}
 *   onClone={() => setCloneModalOpen(true)}
 * />
 * ```
 */
export const ProfileCard = ({
  profile,
  onClick,
  onEdit,
  onClone,
  onDelete,
}: ProfileCardProps) => {
  const handleCardClick = (e: React.MouseEvent) => {
    // Don't trigger card click if clicking buttons
    if ((e.target as HTMLElement).closest('button')) return;
    onClick?.();
  };

  // Determine pass score color
  const getPassScoreColor = (score: number) => {
    if (score >= 70) return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
    if (score >= 50) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';
    return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
  };

  return (
    <Card
      variant="outlined"
      className={`group relative transition-all duration-200 hover:shadow-lg hover:border-blue-200 dark:hover:border-blue-800 ${onClick ? 'cursor-pointer' : ''}`}
      onClick={handleCardClick}
    >
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1.5">
              <h3 className="font-semibold text-gray-900 dark:text-white truncate text-base">
                {profile.name}
              </h3>
              {profile.is_system_template && (
                <Badge variant="info" size="sm">
                  System
                </Badge>
              )}
            </div>
            {profile.description && (
              <Text size="sm" color="muted" className="line-clamp-2">
                {profile.description}
              </Text>
            )}
          </div>
        </div>

        {/* Stats Badges */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {/* Criteria Count Badge */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/30">
            <svg
              className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <span className="text-xs font-medium text-blue-700 dark:text-blue-300">
              {profile.criteria_count} {profile.criteria_count === 1 ? 'criterion' : 'criteria'}
            </span>
          </div>

          {/* Pass Score Badge */}
          <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full ${getPassScoreColor(profile.passing_score)}`}>
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-xs font-medium">
              {profile.passing_score}% to pass
            </span>
          </div>
        </div>

        {/* Actions - Icon buttons in a contained row */}
        <div className="flex items-center justify-end gap-1 pt-3 border-t border-gray-200 dark:border-gray-700">
          {onClone && (
            <button
              onClick={(e) => { e.stopPropagation(); onClone(); }}
              className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-gray-500 hover:text-blue-600 hover:bg-blue-50 dark:text-gray-400 dark:hover:text-blue-400 dark:hover:bg-blue-900/30 transition-colors"
              title="Clone profile"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </button>
          )}
          {onEdit && !profile.is_system_template && (
            <button
              onClick={(e) => { e.stopPropagation(); onEdit(); }}
              className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-gray-500 hover:text-amber-600 hover:bg-amber-50 dark:text-gray-400 dark:hover:text-amber-400 dark:hover:bg-amber-900/30 transition-colors"
              title="Edit profile"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
          )}
          {onDelete && !profile.is_system_template && (
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(); }}
              className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-50 dark:text-gray-400 dark:hover:text-red-400 dark:hover:bg-red-900/30 transition-colors"
              title="Delete profile"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          )}
        </div>
      </div>
    </Card>
  );
};
