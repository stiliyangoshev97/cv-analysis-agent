/**
 * @fileoverview Container Component
 *
 * Layout container component for consistent page width and padding.
 * Provides multiple size variants for different content widths.
 *
 * @module shared/components/ui/Container
 *
 * FEATURES:
 * - 4 size variants (sm, md, lg, full)
 * - Centered content with auto margins
 * - Horizontal padding included
 * - Uses CVA for type-safe variant props
 *
 * SIZE VARIANTS:
 * - sm: max-w-2xl (672px) - narrow content, forms
 * - md: max-w-4xl (896px) - default, most pages
 * - lg: max-w-6xl (1152px) - wide content, dashboards
 * - full: max-w-full - full width with padding
 *
 * @example
 * ```tsx
 * // Default medium container
 * <Container>
 *   <h1>Page Content</h1>
 * </Container>
 *
 * // Small container for forms
 * <Container size="sm">
 *   <LoginForm />
 * </Container>
 *
 * // Large container for dashboard
 * <Container size="lg">
 *   <Dashboard />
 * </Container>
 *
 * // Full width with padding
 * <Container size="full">
 *   <FullWidthContent />
 * </Container>
 * ```
 */

import { cva, type VariantProps } from 'class-variance-authority';
import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../utils';

/**
 * Container variant styles using class-variance-authority.
 */
const containerVariants = cva('mx-auto px-4 w-full', {
  variants: {
    size: {
      sm: 'max-w-2xl',
      md: 'max-w-4xl',
      lg: 'max-w-6xl',
      full: 'max-w-full',
    },
  },
  defaultVariants: {
    size: 'md',
  },
});

/**
 * Container component props.
 */
interface ContainerProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof containerVariants> {
  /** Content to display */
  children: ReactNode;
}

/**
 * Container Component
 *
 * A layout component for consistent page width and centering.
 */
export const Container = ({
  size,
  className,
  children,
  ...props
}: ContainerProps) => {
  return (
    <div className={cn(containerVariants({ size }), className)} {...props}>
      {children}
    </div>
  );
};
