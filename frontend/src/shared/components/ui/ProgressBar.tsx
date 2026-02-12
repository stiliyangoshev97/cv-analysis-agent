/**
 * @fileoverview ProgressBar Component
 *
 * A visual progress indicator for showing completion status.
 * Used for file uploads, loading states, and multi-step processes.
 *
 * @module shared/components/ui/ProgressBar
 *
 * FEATURES:
 * - Smooth animated transitions
 * - Optional percentage label
 * - Configurable max value
 * - Accessible progress indicator
 * - Uses `cn()` utility for class merging
 *
 * @example
 * ```tsx
 * // Basic progress bar
 * <ProgressBar value={50} />
 *
 * // With percentage label
 * <ProgressBar value={75} showLabel />
 *
 * // Custom max value
 * <ProgressBar value={3} max={10} showLabel />
 *
 * // With custom className
 * <ProgressBar value={100} className="h-3" />
 * ```
 */

import { cn } from '../../utils';

/**
 * ProgressBar component props.
 */
interface ProgressBarProps {
  /** Current progress value */
  value: number;
  /** Maximum value (default: 100) */
  max?: number;
  /** Additional CSS classes */
  className?: string;
  /** Show percentage label below bar */
  showLabel?: boolean;
}

/**
 * ProgressBar Component
 *
 * Displays a horizontal bar indicating progress toward completion.
 *
 * @param props - ProgressBar props
 * @returns Progress bar element with optional label
 */
export const ProgressBar = ({
  value,
  max = 100,
  className,
  showLabel = false,
}: ProgressBarProps) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={cn('w-full', className)}>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
      {showLabel && (
        <p className="mt-1 text-sm text-gray-600 text-center">
          {Math.round(percentage)}%
        </p>
      )}
    </div>
  );
};
