/**
 * @fileoverview Criterion Card Component.
 *
 * Displays a single criterion in a compact card format.
 *
 * @module features/profile/components/CriterionCard
 */

import { Card, Badge, Text, Button } from '@/shared/components/ui';
import type { CriterionResponse } from '@/shared/schemas';

interface CriterionCardProps {
  /** Criterion data */
  criterion: CriterionResponse;
  /** Whether card is editable */
  isEditable?: boolean;
  /** Called when edit is clicked */
  onEdit?: () => void;
  /** Called when delete is clicked */
  onDelete?: () => void;
}

/**
 * Criterion Card
 *
 * Displays criterion information with edit/delete actions.
 *
 * @example
 * ```tsx
 * <CriterionCard
 *   criterion={criterion}
 *   isEditable
 *   onEdit={() => setEditingCriterion(criterion)}
 *   onDelete={() => handleDelete(criterion.id)}
 * />
 * ```
 */
export const CriterionCard = ({
  criterion,
  isEditable = false,
  onEdit,
  onDelete,
}: CriterionCardProps) => {
  return (
    <Card variant="outlined" className="p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-medium text-gray-900 dark:text-white truncate">
              {criterion.name}
            </h4>
            {criterion.is_required && (
              <Badge variant="error" size="sm">
                Required
              </Badge>
            )}
          </div>

          {/* Description */}
          {criterion.description && (
            <Text size="sm" color="muted" className="mb-2 line-clamp-2">
              {criterion.description}
            </Text>
          )}

          {/* Points & Keywords */}
          <div className="flex flex-wrap items-center gap-3">
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
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
              <Text size="sm" color="muted">
                {criterion.max_points} points
              </Text>
            </div>

            {criterion.keywords.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {criterion.keywords.slice(0, 3).map((keyword) => (
                  <Badge key={keyword} variant="neutral" size="sm">
                    {keyword}
                  </Badge>
                ))}
                {criterion.keywords.length > 3 && (
                  <Text size="sm" color="muted">
                    +{criterion.keywords.length - 3} more
                  </Text>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        {isEditable && (
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={onEdit}
              aria-label="Edit criterion"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onDelete}
              aria-label="Delete criterion"
              className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};
