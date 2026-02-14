/**
 * @fileoverview Profile Card Component.
 *
 * Displays a single profile summary in a card format.
 *
 * @module features/profile/components/ProfileCard
 */

import type { ProfileSummary } from '@/shared/schemas';
import { Card, Badge, Text, Button } from '@/shared/components/ui';

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

  return (
    <Card
      variant="outlined"
      className={`transition-all hover:shadow-md ${onClick ? 'cursor-pointer' : ''}`}
      onClick={handleCardClick}
    >
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-900 dark:text-white truncate">
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

        {/* Stats */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-1.5">
            <svg
              className="w-4 h-4 text-gray-400"
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
            <Text size="sm" color="muted">
              {profile.criteria_count} criteria
            </Text>
          </div>
          <div className="flex items-center gap-1.5">
            <svg
              className="w-4 h-4 text-gray-400"
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
            <Text size="sm" color="muted">
              Pass: {profile.passing_score}%
            </Text>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3 border-t border-gray-100 dark:border-gray-700">
          {onClone && (
            <Button variant="ghost" size="sm" onClick={onClone}>
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              Clone
            </Button>
          )}
          {onEdit && !profile.is_system_template && (
            <Button variant="ghost" size="sm" onClick={onEdit}>
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Edit
            </Button>
          )}
          {onDelete && !profile.is_system_template && (
            <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700" onClick={onDelete}>
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};
