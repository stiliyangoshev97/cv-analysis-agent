/**
 * @fileoverview Heading Component
 *
 * Typography component for headings (h1-h6) with consistent styling.
 * Provides multiple levels and styling variants.
 *
 * @module shared/components/ui/Heading
 *
 * FEATURES:
 * - 6 heading levels (h1-h6)
 * - Automatic semantic heading level based on `level` prop
 * - Consistent font sizing and weights
 * - Uses CVA for type-safe variant props
 *
 * SIZE BY LEVEL:
 * - h1: text-4xl (36px)
 * - h2: text-3xl (30px)
 * - h3: text-2xl (24px)
 * - h4: text-xl (20px)
 * - h5: text-lg (18px)
 * - h6: text-base (16px)
 *
 * @example
 * ```tsx
 * // Page title
 * <Heading level={1}>CV Screening Agent</Heading>
 *
 * // Section heading
 * <Heading level={2}>Upload Your CV</Heading>
 *
 * // Card title
 * <Heading level={3}>Evaluation Results</Heading>
 *
 * // With custom className
 * <Heading level={2} className="mb-4">
 *   Section Title
 * </Heading>
 * ```
 */

import { cva, type VariantProps } from 'class-variance-authority';
import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../utils';

/**
 * Heading variant styles using class-variance-authority.
 */
const headingVariants = cva('font-bold text-gray-900 dark:text-white', {
  variants: {
    level: {
      1: 'text-4xl tracking-tight',
      2: 'text-3xl tracking-tight',
      3: 'text-2xl',
      4: 'text-xl',
      5: 'text-lg',
      6: 'text-base',
    },
  },
  defaultVariants: {
    level: 2,
  },
});

/**
 * Heading component props.
 */
interface HeadingProps
  extends HTMLAttributes<HTMLHeadingElement>,
    VariantProps<typeof headingVariants> {
  /** Heading level (1-6), determines both style and semantic element */
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  /** Content to display */
  children: ReactNode;
}

/**
 * Heading Component
 *
 * A typography component for headings with consistent styling.
 */
export const Heading = ({
  level = 2,
  className,
  children,
  ...props
}: HeadingProps) => {
  const Tag = `h${level}` as const;

  return (
    <Tag className={cn(headingVariants({ level }), className)} {...props}>
      {children}
    </Tag>
  );
};
