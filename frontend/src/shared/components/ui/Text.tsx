/**
 * @fileoverview Text Component
 *
 * Typography component for body text with multiple variants.
 * Provides consistent text styling across the application.
 *
 * @module shared/components/ui/Text
 *
 * FEATURES:
 * - 4 size variants (xs, sm, base, lg)
 * - 4 color variants (default, muted, error, success)
 * - 3 weight variants (normal, medium, semibold)
 * - Uses CVA for type-safe variant props
 * - Renders as `p` by default, customizable via `as` prop
 *
 * @example
 * ```tsx
 * // Default text
 * <Text>Regular paragraph text</Text>
 *
 * // Muted helper text
 * <Text variant="muted" size="sm">
 *   Additional context
 * </Text>
 *
 * // Error message
 * <Text variant="error" size="sm">
 *   This field is required
 * </Text>
 *
 * // Large bold text
 * <Text size="lg" weight="semibold">
 *   Important information
 * </Text>
 *
 * // Render as span
 * <Text as="span" variant="muted">Inline text</Text>
 * ```
 */

import { cva, type VariantProps } from 'class-variance-authority';
import type { ElementType, HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../utils';

/**
 * Text variant styles using class-variance-authority.
 */
const textVariants = cva('', {
  variants: {
    variant: {
      default: 'text-gray-900',
      muted: 'text-gray-500',
      error: 'text-red-600',
      success: 'text-green-600',
    },
    size: {
      xs: 'text-xs',
      sm: 'text-sm',
      base: 'text-base',
      lg: 'text-lg',
    },
    weight: {
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
    },
  },
  defaultVariants: {
    variant: 'default',
    size: 'base',
    weight: 'normal',
  },
});

/**
 * Text component props.
 */
interface TextProps
  extends HTMLAttributes<HTMLParagraphElement>,
    VariantProps<typeof textVariants> {
  /** Content to display */
  children: ReactNode;
  /** HTML element to render as (default: 'p') */
  as?: ElementType;
}

/**
 * Text Component
 *
 * A typography component for body text with consistent styling.
 */
export const Text = ({
  variant,
  size,
  weight,
  className,
  children,
  as: Component = 'p',
  ...props
}: TextProps) => {
  return (
    <Component
      className={cn(textVariants({ variant, size, weight }), className)}
      {...props}
    >
      {children}
    </Component>
  );
};
