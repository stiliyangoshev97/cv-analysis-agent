/**
 * @fileoverview Card Component
 *
 * Flexible container component with multiple variants for content grouping.
 * Includes sub-components for structured content layout.
 *
 * @module shared/components/ui/Card
 *
 * FEATURES:
 * - 3 visual variants (default, hover, outlined)
 * - 4 padding options (none, sm, md, lg)
 * - Hover effects for interactive cards
 * - Sub-components (Header, Title, Description, Content, Footer)
 * - Uses CVA for type-safe variant props
 *
 * VARIANTS:
 * - default: White background with border and shadow
 * - hover: Interactive card with hover lift effect
 * - outlined: Transparent with visible border only
 *
 * SUB-COMPONENTS:
 * - CardHeader: Container for title + description
 * - CardTitle: Styled h3 heading
 * - CardDescription: Muted text below title
 * - CardContent: Main content area
 * - CardFooter: Bottom section with top border
 *
 * @example
 * ```tsx
 * // Simple card
 * <Card>
 *   <p>Card content here</p>
 * </Card>
 *
 * // Card with structured content
 * <Card>
 *   <CardHeader>
 *     <CardTitle>CV Evaluation</CardTitle>
 *     <CardDescription>AI-powered resume analysis</CardDescription>
 *   </CardHeader>
 *   <CardContent>
 *     <p>Main content here</p>
 *   </CardContent>
 *   <CardFooter>
 *     <Button>View Details</Button>
 *   </CardFooter>
 * </Card>
 *
 * // Hover card (clickable)
 * <Card variant="hover" onClick={handleClick}>
 *   <CardTitle>Click me</CardTitle>
 * </Card>
 * ```
 */

import { cva, type VariantProps } from 'class-variance-authority';
import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../utils';

/**
 * Card variant styles using class-variance-authority.
 */
const cardVariants = cva('rounded-xl transition-colors', {
  variants: {
    variant: {
      default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm',
      hover: `bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm
              transition-all duration-200 hover:border-gray-300 dark:hover:border-gray-600
              hover:shadow-md hover:-translate-y-0.5 cursor-pointer`,
      outlined: 'bg-transparent border border-gray-300 dark:border-gray-600',
    },
    padding: {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    },
  },
  defaultVariants: {
    variant: 'default',
    padding: 'md',
  },
});

/**
 * Card component props.
 */
interface CardProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  /** Card content */
  children: ReactNode;
}

/**
 * Card Component
 *
 * A container for grouping related content with visual separation.
 */
export const Card = ({ variant, padding, className, children, ...props }: CardProps) => {
  return (
    <div className={cn(cardVariants({ variant, padding }), className)} {...props}>
      {children}
    </div>
  );
};

/**
 * CardHeader component props.
 */
interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

/**
 * CardHeader Component
 *
 * Container for card title and description. Adds bottom margin.
 */
export const CardHeader = ({ className, children, ...props }: CardHeaderProps) => {
  return (
    <div className={cn('mb-4', className)} {...props}>
      {children}
    </div>
  );
};

/**
 * CardTitle component props.
 */
interface CardTitleProps extends HTMLAttributes<HTMLHeadingElement> {
  children: ReactNode;
}

/**
 * CardTitle Component
 *
 * Styled h3 heading for card titles.
 */
export const CardTitle = ({ className, children, ...props }: CardTitleProps) => {
  return (
    <h3 className={cn('text-lg font-semibold text-gray-900 dark:text-white', className)} {...props}>
      {children}
    </h3>
  );
};

/**
 * CardDescription component props.
 */
interface CardDescriptionProps extends HTMLAttributes<HTMLParagraphElement> {
  children: ReactNode;
}

/**
 * CardDescription Component
 *
 * Muted text for card subtitles/descriptions.
 */
export const CardDescription = ({ className, children, ...props }: CardDescriptionProps) => {
  return (
    <p className={cn('text-sm text-gray-500 dark:text-gray-400 mt-1', className)} {...props}>
      {children}
    </p>
  );
};

/**
 * CardContent component props.
 */
interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

/**
 * CardContent Component
 *
 * Main content area of the card.
 */
export const CardContent = ({ className, children, ...props }: CardContentProps) => {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
};

/**
 * CardFooter component props.
 */
interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

/**
 * CardFooter Component
 *
 * Bottom section of card, typically for actions. Includes top border.
 */
export const CardFooter = ({ className, children, ...props }: CardFooterProps) => {
  return (
    <div className={cn('mt-4 pt-4 border-t border-gray-100 dark:border-gray-700', className)} {...props}>
      {children}
    </div>
  );
};
