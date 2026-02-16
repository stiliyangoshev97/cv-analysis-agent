/**
 * @fileoverview Page Loader Component
 *
 * Full-page loading indicator used as Suspense fallback for lazy-loaded routes.
 * Provides a smooth loading experience during code-splitting chunk loads.
 *
 * @module shared/components/ui/PageLoader
 *
 * @example
 * ```tsx
 * <Suspense fallback={<PageLoader />}>
 *   <LazyPage />
 * </Suspense>
 * ```
 */

import { Spinner } from './Spinner';

/**
 * Page Loader Component
 *
 * Centered loading spinner for route transitions.
 * Used as fallback for React.lazy() loaded components.
 */
export const PageLoader = () => {
  return (
    <div className="flex items-center justify-center min-h-[400px] w-full">
      <div className="flex flex-col items-center gap-4">
        <Spinner size="lg" className="text-blue-600 dark:text-blue-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400 animate-pulse">
          Loading...
        </p>
      </div>
    </div>
  );
};
