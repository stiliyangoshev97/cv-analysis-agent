/**
 * @fileoverview Protected route guard component.
 *
 * Shows auth page if user is not authenticated.
 * Shows children if authenticated.
 *
 * @module router/guards/ProtectedRoute
 */

import { useAuthState } from '@/features/auth/hooks';
import { AuthPage } from '@/features/auth/components';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * Wrapper component that protects routes from unauthenticated access.
 *
 * @param props - Component props
 * @param props.children - Protected content to render when authenticated
 * @returns Auth page if not authenticated, children otherwise
 *
 * @example
 * ```tsx
 * <ProtectedRoute>
 *   <Dashboard />
 * </ProtectedRoute>
 * ```
 */
export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useAuthState();

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-gray-600">Loading...</span>
        </div>
      </div>
    );
  }

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage />;
  }

  // Show protected content
  return <>{children}</>;
};
