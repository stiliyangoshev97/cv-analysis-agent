/**
 * @fileoverview Toast Notification Component
 *
 * Provides toast notifications using Sonner.
 * Includes a ToastProvider and toast utility functions.
 *
 * @module shared/components/ui/Toast
 */

import { Toaster, toast as sonnerToast } from 'sonner';

/**
 * Toast Provider Component
 *
 * Wraps the app to enable toast notifications.
 * Should be placed near the root of the app.
 *
 * @example
 * ```tsx
 * <ToastProvider />
 * ```
 */
export const ToastProvider = () => {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        classNames: {
          toast: 'bg-white border border-gray-200 shadow-lg rounded-lg',
          title: 'text-gray-900 font-medium',
          description: 'text-gray-600 text-sm',
          success: 'border-green-200 bg-green-50',
          error: 'border-red-200 bg-red-50',
          warning: 'border-amber-200 bg-amber-50',
          info: 'border-blue-200 bg-blue-50',
        },
      }}
      expand
      richColors
      closeButton
    />
  );
};

/**
 * Toast utility object with typed methods.
 *
 * @example
 * ```tsx
 * import { toast } from '@/shared/components';
 *
 * toast.success('Operation completed!');
 * toast.error('Something went wrong');
 * toast.info('Here is some info');
 * toast.warning('Be careful!');
 * ```
 */
export const toast = {
  /** Show a success toast */
  success: (message: string, description?: string) => {
    sonnerToast.success(message, { description });
  },

  /** Show an error toast */
  error: (message: string, description?: string) => {
    sonnerToast.error(message, { description });
  },

  /** Show an info toast */
  info: (message: string, description?: string) => {
    sonnerToast.info(message, { description });
  },

  /** Show a warning toast */
  warning: (message: string, description?: string) => {
    sonnerToast.warning(message, { description });
  },

  /** Show a loading toast that can be updated */
  loading: (message: string) => {
    return sonnerToast.loading(message);
  },

  /** Update or dismiss a toast */
  dismiss: (id?: string | number) => {
    sonnerToast.dismiss(id);
  },

  /** Show a promise toast */
  promise: <T,>(
    promise: Promise<T>,
    options: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((error: Error) => string);
    }
  ) => {
    return sonnerToast.promise(promise, options);
  },
};
