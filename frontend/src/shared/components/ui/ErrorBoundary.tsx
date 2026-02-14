/**
 * @fileoverview Error Boundary Component
 *
 * Catches JavaScript errors in child components and displays
 * a fallback UI instead of crashing the entire app.
 *
 * @module shared/components/ui/ErrorBoundary
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
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
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <svg
              className="w-8 h-8 text-red-600"
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
            <div className="mb-6 p-4 bg-gray-100 rounded-lg text-left max-w-lg overflow-auto">
              <Text size="sm" className="font-mono text-red-600">
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
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-8 text-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <svg
              className="w-10 h-10 text-red-600"
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
