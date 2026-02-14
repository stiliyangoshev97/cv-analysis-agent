/**
 * @fileoverview Error Boundary Component
 *
 * Catches JavaScript errors in child components and displays
 * a fallback UI instead of crashing the entire app.
 *
 * @module shared/components/ui/ErrorBoundary
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { useRouteError, isRouteErrorResponse, useNavigate } from 'react-router-dom';
import { Button } from './Button';
import { Heading } from './Heading';
import { Text } from './Text';

interface ErrorBoundaryProps {
  /** Child components to wrap */
  children: ReactNode;
  /** Optional fallback component */
  fallback?: ReactNode;
  /** Callback when error occurs */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary Component
 *
 * Catches errors in child components and displays a fallback UI.
 *
 * @example
 * ```tsx
 * <ErrorBoundary>
 *   <MyComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mb-6">
            <svg
              className="w-8 h-8 text-red-600 dark:text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <Heading level={3} className="mb-2">
            Something went wrong
          </Heading>
          <Text color="muted" className="mb-6 max-w-md">
            We're sorry, but something unexpected happened. Please try again or refresh the page.
          </Text>
          {import.meta.env.DEV && this.state.error && (
            <div className="mb-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-left max-w-lg overflow-auto">
              <Text size="sm" className="font-mono text-red-600 dark:text-red-400">
                {this.state.error.message}
              </Text>
            </div>
          )}
          <div className="flex gap-3">
            <Button variant="outline" onClick={this.handleReset}>
              Try Again
            </Button>
            <Button variant="primary" onClick={this.handleReload}>
              Reload Page
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Page Error Boundary
 *
 * A full-page error boundary with navigation option.
 */
export const PageErrorBoundary = ({ children }: { children: ReactNode }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900 p-8 text-center">
          <div className="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mb-6">
            <svg
              className="w-10 h-10 text-red-600 dark:text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <Heading level={2} className="mb-2">
            Oops! Page Error
          </Heading>
          <Text color="muted" className="mb-8 max-w-md">
            Something went wrong loading this page. Please try refreshing or go back to the home page.
          </Text>
          <div className="flex gap-4">
            <Button variant="outline" onClick={() => window.history.back()}>
              Go Back
            </Button>
            <Button variant="primary" onClick={() => window.location.href = '/'}>
              Home Page
            </Button>
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
};

/**
 * Route Error Boundary
 *
 * Error element for React Router that displays a beautiful error page.
 * Use as `errorElement` prop in route definitions.
 *
 * @example
 * ```tsx
 * {
 *   path: '/settings',
 *   element: <SettingsPage />,
 *   errorElement: <RouteErrorBoundary />
 * }
 * ```
 */
export const RouteErrorBoundary = () => {
  const error = useRouteError();
  const navigate = useNavigate();

  // Extract error message
  let errorMessage = 'An unexpected error occurred';
  let errorStatus = '';

  if (isRouteErrorResponse(error)) {
    errorStatus = `${error.status}`;
    errorMessage = error.statusText || error.data?.message || 'Page not found';
  } else if (error instanceof Error) {
    errorMessage = error.message;
  } else if (typeof error === 'string') {
    errorMessage = error;
  }

  // Log error in development
  if (import.meta.env.DEV) {
    console.error('Route error:', error);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8 text-center">
      {/* Error Icon */}
      <div className="relative mb-8">
        <div className="w-24 h-24 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
          <svg
            className="w-12 h-12 text-red-500 dark:text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        {errorStatus && (
          <div className="absolute -top-2 -right-2 w-10 h-10 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-lg">
            {errorStatus}
          </div>
        )}
      </div>

      {/* Error Message */}
      <Heading level={1} className="mb-3 text-gray-900 dark:text-white">
        Something went wrong
      </Heading>
      <Text color="muted" className="mb-2 max-w-md text-lg">
        We apologize for the inconvenience.
      </Text>

      {/* Error Details (Dev Mode) */}
      {import.meta.env.DEV && (
        <div className="mb-8 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl max-w-lg w-full">
          <Text size="sm" className="font-mono text-red-700 dark:text-red-300 break-words">
            {errorMessage}
          </Text>
        </div>
      )}

      {/* Production Message */}
      {!import.meta.env.DEV && (
        <Text color="muted" className="mb-8 max-w-md">
          {errorMessage}
        </Text>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          variant="outline"
          onClick={() => navigate(-1)}
          className="min-w-[140px]"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Go Back
        </Button>
        <Button
          variant="primary"
          onClick={() => navigate('/')}
          className="min-w-[140px]"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Home Page
        </Button>
        <Button
          variant="secondary"
          onClick={() => window.location.reload()}
          className="min-w-[140px]"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Reload
        </Button>
      </div>

      {/* Footer */}
      <Text size="sm" color="muted" className="mt-12">
        If this problem persists, please contact support.
      </Text>
    </div>
  );
};
