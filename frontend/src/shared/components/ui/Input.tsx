/**
 * @fileoverview Input Component
 *
 * Styled input field with label, error, and helper text support.
 * Uses forwardRef for React Hook Form compatibility.
 *
 * @module shared/components/ui/Input
 *
 * FEATURES:
 * - Automatic label + input ID association
 * - Error state with red border and message
 * - Helper text for additional context
 * - Focus ring animation
 * - Disabled state styling
 * - forwardRef for React Hook Form integration
 *
 * REACT HOOK FORM:
 * ```tsx
 * const { register, formState: { errors } } = useForm();
 *
 * <Input
 *   label="Email"
 *   type="email"
 *   error={errors.email?.message}
 *   {...register('email')}
 * />
 * ```
 *
 * @example
 * ```tsx
 * // Basic input with label
 * <Input label="Username" placeholder="Enter username" />
 *
 * // Input with error
 * <Input
 *   label="Email"
 *   error="Email is required"
 *   placeholder="your@email.com"
 * />
 *
 * // Input with helper text
 * <Input
 *   label="Password"
 *   type="password"
 *   helperText="Must be at least 8 characters"
 * />
 *
 * // Disabled input
 * <Input label="Read Only" value="Fixed value" disabled />
 * ```
 */

import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '../../utils';

/**
 * Input component props.
 */
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** Label text displayed above the input */
  label?: string;
  /** Error message (shows below input in red) */
  error?: string;
  /** Helper text for additional context */
  helperText?: string;
}

/**
 * Input Component
 *
 * A styled input field with label, error, and helper text support.
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full px-3 py-2 rounded-lg border bg-white text-gray-900',
            'placeholder:text-gray-400',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50',
            'transition-colors duration-200',
            error
              ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20'
              : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500/20',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
