/**
 * @fileoverview Badge Component
 *
 * Small status indicator labels with color-coded variants.
 * Used to show status, categories, and metadata throughout the app.
 *
 * @module shared/components/ui/Badge
 *
 * FEATURES:
 * - 5 color variants (success, error, warning, info, neutral)
 * - 3 size options (sm, md, lg)
 * - Pill-shaped design (rounded-full)
 * - Uses CVA for type-safe variant props
 *
 * VARIANTS:
 * - success: Green for positive states (Pass, Verified, Complete)
 * - error: Red for negative states (Fail, Rejected, High Risk)
 * - warning: Yellow for caution (Pending, Medium Risk)
 * - info: Blue for informational (New, Featured)
 * - neutral: Gray for neutral/default states
 *
 * @example
 * ```tsx
 * // Success badge for pass status
 * <Badge variant="success">Pass</Badge>
 *
 * // Error badge for fail status
 * <Badge variant="error">Fail</Badge>
 *
 * // Small warning badge
 * <Badge variant="warning" size="sm">Pending</Badge>
 *
 * // With custom className
 * <Badge variant="info" className="ml-2">New</Badge>
 * ```
 */

import { cva, type VariantProps } from 'class-variance-authority';
import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../utils';

/**
 * Badge variant styles using class-variance-authority.
 */
const badgeVariants = cva(
  'inline-flex items-center font-medium rounded-full',
  {
    variants: {
      variant: {
        success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        error: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
        warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
        info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        neutral: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-2.5 py-1 text-sm',
        lg: 'px-3 py-1.5 text-base',
      },
    },
    defaultVariants: {
      variant: 'neutral',
      size: 'md',
    },
  }
);

/**
 * Badge component props.
 * Extends native span attributes with variant props.
 */
interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  /** Badge content (text, icons, etc) */
  children: ReactNode;
}

/**
 * Badge Component
 *
 * A small label for displaying status or category information.
 *
 * @param props - Badge props including variant, size, and content
 * @returns Styled span element
 */
export const Badge = ({ variant, size, className, children, ...props }: BadgeProps) => {
  return (
    <span className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {children}
    </span>
  );
};
