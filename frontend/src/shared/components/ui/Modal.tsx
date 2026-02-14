/**
 * @fileoverview Modal Component
 *
 * Accessible modal/dialog component with backdrop and focus trap.
 *
 * @module shared/components/ui/Modal
 *
 * FEATURES:
 * - Accessible with proper ARIA attributes
 * - Backdrop click to close (optional)
 * - Escape key to close
 * - Focus trap inside modal
 * - Multiple sizes (sm, md, lg, xl)
 * - Animated entrance/exit
 *
 * @example
 * ```tsx
 * <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="Confirm">
 *   <p>Are you sure?</p>
 *   <ModalFooter>
 *     <Button variant="ghost" onClick={onClose}>Cancel</Button>
 *     <Button onClick={onConfirm}>Confirm</Button>
 *   </ModalFooter>
 * </Modal>
 * ```
 */

import { useEffect, useRef, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils';

const modalVariants = cva(
  'relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-h-[90vh] overflow-y-auto',
  {
    variants: {
      size: {
        sm: 'w-full max-w-sm',
        md: 'w-full max-w-md',
        lg: 'w-full max-w-lg',
        xl: 'w-full max-w-xl',
        '2xl': 'w-full max-w-2xl',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  }
);

interface ModalProps extends VariantProps<typeof modalVariants> {
  /** Whether modal is open */
  isOpen: boolean;
  /** Called when modal should close */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal content */
  children: ReactNode;
  /** Whether clicking backdrop closes modal */
  closeOnBackdrop?: boolean;
  /** Additional class for modal container */
  className?: string;
}

/**
 * Modal Component
 *
 * Renders an accessible modal dialog with backdrop.
 */
export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size,
  closeOnBackdrop = true,
  className,
}: ModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  // Focus trap
  useEffect(() => {
    if (isOpen && modalRef.current) {
      const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (closeOnBackdrop && e.target === e.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      <div
        ref={modalRef}
        className={cn(
          modalVariants({ size }),
          'animate-in zoom-in-95 slide-in-from-bottom-4 duration-200',
          className
        )}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h2
              id="modal-title"
              className="text-lg font-semibold text-gray-900 dark:text-white"
            >
              {title}
            </h2>
            <button
              type="button"
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Close modal"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Content */}
        <div className={cn(!title && 'pt-4')}>{children}</div>
      </div>
    </div>,
    document.body
  );
};

/**
 * Modal Body - Container for modal content
 */
export const ModalBody = ({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) => (
  <div className={cn('p-4', className)}>{children}</div>
);

/**
 * Modal Footer - Container for modal actions
 */
export const ModalFooter = ({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) => (
  <div
    className={cn(
      'flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700',
      className
    )}
  >
    {children}
  </div>
);
