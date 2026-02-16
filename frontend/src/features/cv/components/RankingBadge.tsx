/**
 * @fileoverview CV Ranking Badge component.
 *
 * Displays percentile ranking for a CV with visual indicator.
 *
 * @module features/cv/components/RankingBadge
 */

import { Badge, Spinner, Text } from '@/shared/components/ui';
import { useCVRanking } from '../hooks';

// =============================================================================
// Props
// =============================================================================

interface RankingBadgeProps {
  /** The CV ID to get ranking for */
  cvId: string;
  /** Whether to show detailed info (rank + total) */
  showDetails?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Badge showing CV ranking/percentile.
 *
 * @example
 * ```tsx
 * <RankingBadge cvId="uuid" showDetails />
 * // Displays: "Top 10% • #3 of 25"
 * ```
 */
export const RankingBadge = ({
  cvId,
  showDetails = false,
  size = 'sm',
}: RankingBadgeProps) => {
  const { data: ranking, isLoading, error } = useCVRanking(cvId);

  if (isLoading) {
    return (
      <div className="inline-flex items-center gap-1">
        <Spinner size="sm" />
      </div>
    );
  }

  if (error || !ranking) {
    return null;
  }

  // Determine badge color based on percentile
  let variant: 'success' | 'warning' | 'neutral' | 'info' = 'neutral';
  let icon: React.ReactNode = null;

  if (ranking.percentile >= 90) {
    variant = 'success';
    icon = (
      <svg
        className="w-3 h-3"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    );
  } else if (ranking.percentile >= 75) {
    variant = 'info';
  } else if (ranking.percentile >= 50) {
    variant = 'warning';
  }

  return (
    <div className="inline-flex items-center gap-2">
      <Badge variant={variant} size={size} className="inline-flex items-center gap-1">
        {icon}
        {ranking.label}
      </Badge>
      
      {showDetails && (
        <Text size="sm" color="muted">
          #{ranking.rank} of {ranking.total_cvs}
        </Text>
      )}
    </div>
  );
};

/**
 * Inline ranking display for compact spaces.
 *
 * @example
 * ```tsx
 * <RankingInline cvId="uuid" />
 * // Displays: "Top 10%"
 * ```
 */
export const RankingInline = ({ cvId }: { cvId: string }) => {
  const { data: ranking, isLoading } = useCVRanking(cvId);

  if (isLoading || !ranking) {
    return null;
  }

  let colorClass = 'text-gray-500 dark:text-gray-400';
  if (ranking.percentile >= 90) {
    colorClass = 'text-green-600 dark:text-green-400';
  } else if (ranking.percentile >= 75) {
    colorClass = 'text-blue-600 dark:text-blue-400';
  } else if (ranking.percentile >= 50) {
    colorClass = 'text-yellow-600 dark:text-yellow-400';
  }

  return (
    <span className={`text-xs font-medium ${colorClass}`}>
      {ranking.label}
    </span>
  );
};
