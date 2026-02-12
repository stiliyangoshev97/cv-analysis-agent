/**
 * @fileoverview Spinner Component
 *
 * Loading spinner indicator for async operations.
 * Provides multiple size variants for different contexts.
 *
 * @module shared/components/ui/Spinner
 *
 * FEATURES:
 * - 4 size variants (xs, sm, md, lg)
 * - Smooth spinning animation
 * - Accessible with aria-label
 * - Uses CVA for type-safe variant props
 *
 * @example
 * ```tsx
 * // Default medium spinner
 * <Spinner />
 *
 * // Small spinner (inline with text)
 * <Spinner size="sm" />
 *
 * // Large spinner (page loading)
 * <Spinner size="lg" />
 *
 * // With custom className
 * <Spinner size="md" className="text-blue-600" />
 * ```
 */

import { cva, type VariantProps } from 'class-variance-authority';
import type { HTMLAttributes } from 'react';
import { cn } from '../../utils';

/**
 * Spinner variant styles using class-variance-authority.
 */
const spinnerVariants = cva(
  'animate-spin rounded-full border-2 border-current border-t-transparent',
  {
    variants: {
      size: {
        xs: 'h-3 w-3',
        sm: 'h-4 w-4',
        md: 'h-6 w-6',
        lg: 'h-8 w-8',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  }
);

/**
 * Spinner component props.
 */
interface SpinnerProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof spinnerVariants> {}

/**
 * Spinner Component
 *
 * A loading indicator with spinning animation.
 */
export const Spinner = ({ size, className, ...props }: SpinnerProps) => {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn(spinnerVariants({ size }), className)}
      {...props}
    />
  );
};
