/**
 * @fileoverview Textarea Component
 *
 * Styled multi-line text input with label, error, and helper text support.
 * Uses forwardRef for React Hook Form compatibility.
 *
 * @module shared/components/ui/Textarea
 *
 * FEATURES:
 * - Automatic label + textarea ID association
 * - Error state with red border and message
 * - Helper text for additional context
 * - Configurable rows (defaults to 4)
 * - Focus ring animation
 * - Disabled state styling
 * - forwardRef for React Hook Form integration
 *
 * @example
 * ```tsx
 * // Basic textarea
 * <Textarea placeholder="Enter description..." />
 *
 * // With label and helper text
 * <Textarea
 *   label="Description"
 *   helperText="Describe your experience"
 *   placeholder="Enter details..."
 * />
 *
 * // With error state
 * <Textarea
 *   label="Content"
 *   error="Content is required"
 * />
 *
 * // Custom rows
 * <Textarea
 *   label="Long Description"
 *   rows={8}
 * />
 *
 * // With React Hook Form
 * <Textarea
 *   label="Bio"
 *   {...register('bio')}
 *   error={errors.bio?.message}
 * />
 * ```
 */

import { forwardRef, type TextareaHTMLAttributes } from 'react';
import { cn } from '../../utils';

/**
 * Textarea component props.
 */
interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  /** Label text displayed above the textarea */
  label?: string;
  /** Error message (shows below textarea in red) */
  error?: string;
  /** Helper text for additional context */
  helperText?: string;
}

/**
 * Textarea Component
 *
 * A styled multi-line text input with label and error support.
 */
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helperText, className, id, rows = 4, ...props }, ref) => {
    const textareaId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          rows={rows}
          className={cn(
            'w-full px-3 py-2 rounded-lg border bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none',
            'placeholder:text-gray-400 dark:placeholder:text-gray-500',
            'focus:outline-none focus:ring-2 focus:ring-offset-0 dark:focus:ring-offset-gray-900',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 dark:disabled:bg-gray-900',
            'transition-colors duration-200',
            error
              ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20'
              : 'border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:ring-blue-500/20',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
