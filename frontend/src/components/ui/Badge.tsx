import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';
import type { ReactNode } from 'react';

const badgeVariants = cva(
  'inline-flex items-center font-medium rounded-full',
  {
    variants: {
      variant: {
        success: 'bg-green-100 text-green-800',
        error: 'bg-red-100 text-red-800',
        warning: 'bg-yellow-100 text-yellow-800',
        info: 'bg-blue-100 text-blue-800',
        neutral: 'bg-gray-100 text-gray-800',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-2.5 py-1 text-sm',
        lg: 'px-3 py-1.5 text-base',
      },
    },
    defaultVariants: {
      variant: 'neutral',
      size: 'md',
    },
  }
);

interface BadgeProps extends VariantProps<typeof badgeVariants> {
  children: ReactNode;
  className?: string;
}

export const Badge = ({ variant, size, className, children }: BadgeProps) => {
  return (
    <span className={clsx(badgeVariants({ variant, size }), className)}>
      {children}
    </span>
  );
};
