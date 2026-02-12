/**
 * @fileoverview Barrel export for shared utilities.
 * @module shared/utils
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility function to merge Tailwind CSS classes.
 * Combines clsx and tailwind-merge for optimal class handling.
 *
 * @param inputs - Class values to merge
 * @returns Merged class string
 *
 * @example
 * ```typescript
 * cn('px-4 py-2', isActive && 'bg-blue-500', className)
 * ```
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
