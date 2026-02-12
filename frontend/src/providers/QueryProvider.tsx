/**
 * @fileoverview React Query provider configuration.
 * 
 * Configures TanStack Query with default options for the application.
 * 
 * @module providers/QueryProvider
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';

/**
 * Pre-configured QueryClient instance.
 * 
 * Default options:
 * - retry: 1 (retry failed requests once)
 * - refetchOnWindowFocus: false (don't refetch when window regains focus)
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

interface QueryProviderProps {
  children: ReactNode;
}

/**
 * Query provider component wrapping TanStack Query.
 * 
 * @param props - Component props
 * @param props.children - Child components to wrap
 * @returns QueryClientProvider with configured client
 * 
 * @example
 * ```tsx
 * <QueryProvider>
 *   <App />
 * </QueryProvider>
 * ```
 */
export const QueryProvider = ({ children }: QueryProviderProps) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};
