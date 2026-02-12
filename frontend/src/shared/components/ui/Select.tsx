/**
 * @fileoverview Select Component
 *
 * Styled dropdown select with custom arrow icon and label support.
 * Uses forwardRef for React Hook Form compatibility.
 *
 * @module shared/components/ui/Select
 *
 * FEATURES:
 * - Custom dropdown arrow (hidden native arrow)
 * - Automatic label + select ID association
 * - Error state with red border and message
 * - Placeholder option support
 * - Focus ring animation
 * - Disabled state styling
 * - forwardRef for React Hook Form integration
 *
 * OPTIONS FORMAT:
 * ```tsx
 * const options = [
 *   { value: 'low', label: 'Low' },
 *   { value: 'medium', label: 'Medium' },
 *   { value: 'high', label: 'High' },
 * ];
 * ```
 *
 * @example
 * ```tsx
 * // Basic select with label
 * <Select
 *   label="Risk Level"
 *   options={[
 *     { value: 'low', label: 'Low' },
 *     { value: 'medium', label: 'Medium' },
 *     { value: 'high', label: 'High' },
 *   ]}
 * />
 *
 * // With placeholder
 * <Select
 *   label="Category"
 *   placeholder="Select a category..."
 *   options={categories}
 * />
 *
 * // With error
 * <Select
 *   label="Category"
 *   options={categories}
 *   error="Please select a category"
 * />
 *
 * // With React Hook Form
 * <Select
 *   label="Status"
 *   options={statusOptions}
 *   {...register('status')}
 *   error={errors.status?.message}
 * />
 * ```
 */

import { forwardRef, type SelectHTMLAttributes } from 'react';
import { cn } from '../../utils';

/**
 * Option type for select dropdown.
 */
interface SelectOption {
  /** Option value */
  value: string;
  /** Display label */
  label: string;
}

/**
 * Select component props.
 */
interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  /** Label text displayed above the select */
  label?: string;
  /** Error message (shows below select in red) */
  error?: string;
  /** Array of options with value and label */
  options: SelectOption[];
  /** Placeholder text shown when no option is selected */
  placeholder?: string;
}

/**
 * Select Component
 *
 * A styled dropdown select with custom arrow and label support.
 */
export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, placeholder, className, id, ...props }, ref) => {
    const selectId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={selectId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            className={cn(
              'w-full px-3 py-2 rounded-lg border bg-white text-gray-900',
              'appearance-none cursor-pointer pr-10',
              'focus:outline-none focus:ring-2 focus:ring-offset-0',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50',
              'transition-colors duration-200',
              error
                ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20'
                : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500/20',
              className
            )}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {/* Custom dropdown arrow */}
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
            <svg
              className="h-4 w-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
