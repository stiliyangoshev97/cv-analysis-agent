/**
 * @fileoverview Toggle switch component.
 *
 * A beautiful animated toggle switch for boolean settings.
 *
 * @module features/notification/components/Toggle
 */

import { cn } from '@/shared/utils';

interface ToggleProps {
  /** Whether the toggle is on */
  checked: boolean;
  /** Callback when toggle changes */
  onChange: (checked: boolean) => void;
  /** Whether the toggle is disabled */
  disabled?: boolean;
  /** Accessible label */
  label?: string;
}

/**
 * Toggle switch component.
 *
 * @example
 * ```tsx
 * <Toggle
 *   checked={emailEnabled}
 *   onChange={setEmailEnabled}
 *   label="Enable email notifications"
 * />
 * ```
 */
export const Toggle = ({ checked, onChange, disabled, label }: ToggleProps) => {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      disabled={disabled}
      onClick={() => !disabled && onChange(!checked)}
      className={cn(
        'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2',
        checked ? 'bg-indigo-600' : 'bg-gray-200',
        disabled && 'cursor-not-allowed opacity-50'
      )}
    >
      <span
        className={cn(
          'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
          checked ? 'translate-x-5' : 'translate-x-0'
        )}
      />
    </button>
  );
};
