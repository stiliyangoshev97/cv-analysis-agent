/**
 * @fileoverview Button Component
 *
 * Reusable button component with multiple variants using class-variance-authority.
 * Designed for the CV Screening Agent with a clean, professional light theme.
 *
 * @module shared/components/ui/Button
 *
 * FEATURES:
 * - 5 visual variants (primary, secondary, outline, ghost, danger)
 * - 3 size options (sm, md, lg)
 * - Loading state support
 * - Disabled state styling
 * - Uses CVA for type-safe variant props
 * - Uses `cn()` utility for class merging
 *
 * VARIANTS:
 * - primary: Blue button for main CTAs (Upload, Submit)
 * - secondary: Gray button for secondary actions
 * - outline: Bordered button for tertiary actions
 * - ghost: Transparent button for subtle actions (Dismiss, Cancel)
 * - danger: Red button for destructive actions (Delete, Sign Out)
 *
 * SIZES:
 * - sm: Small (px-3 py-1.5) - for inline/compact buttons
 * - md: Medium (px-4 py-2) - default, most common
 * - lg: Large (px-6 py-3) - for hero CTAs
 *
 * @example
 * ```tsx
 * // Primary button (default)
 * <Button onClick={handleClick}>Upload CV</Button>
 *
 * // With loading state
 * <Button isLoading={isSubmitting} disabled={isSubmitting}>
 *   Submit
 * </Button>
 *
 * // Danger button for logout
 * <Button variant="danger" onClick={logout}>Sign Out</Button>
 *
 * // Small ghost button
 * <Button variant="ghost" size="sm">Cancel</Button>
 *
 * // Large CTA
 * <Button size="lg" variant="primary">Get Started</Button>
 * ```
 */

import { cva, type VariantProps } from 'class-variance-authority';
import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '../../utils';

/**
 * Button variant styles using class-variance-authority.
 * Defines all possible visual combinations.
 */
const buttonVariants = cva(
  'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed dark:focus:ring-offset-gray-900',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 dark:bg-blue-500 dark:hover:bg-blue-600',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600',
        outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700',
        ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800',
        danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 dark:bg-red-500 dark:hover:bg-red-600',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm rounded-md',
        md: 'px-4 py-2 text-sm rounded-lg',
        lg: 'px-6 py-3 text-base rounded-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

/**
 * Button component props.
 * Extends native button attributes with variant props.
 */
interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /** Button content (text, icons, etc) */
  children: ReactNode;
  /** Show loading spinner and disable button */
  isLoading?: boolean;
}

/**
 * Button Component
 *
 * A versatile button with multiple visual variants and sizes.
 *
 * @param props - Button props including variant, size, and native button attributes
 * @returns Styled button element
 */
export const Button = ({
  variant,
  size,
  className,
  children,
  isLoading,
  disabled,
  ...props
}: ButtonProps) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          {children}
        </span>
      ) : (
        children
      )}
    </button>
  );
};
