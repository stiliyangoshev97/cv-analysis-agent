/**
 * @fileoverview Root layout component.
 *
 * Provides the main application layout with header and footer.
 * Uses shared Container and Text components for consistent styling.
 *
 * @module router/RootLayout
 */

import { Link } from 'react-router-dom';
import { UserMenu } from '@/features/auth';
import { Container, Text, Heading } from '@/shared/components/ui';

/**
 * RootLayout component props.
 */
interface RootLayoutProps {
  /** Page content to render */
  children: React.ReactNode;
}

/**
 * RootLayout Component
 *
 * Wraps all pages with consistent header, content area, and footer.
 *
 * @param props - Component props
 * @returns Layout wrapper element
 */
export const RootLayout = ({ children }: RootLayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <Container className="py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div>
                <Heading level={4} className="text-xl">CV Screening Agent</Heading>
                <Text variant="muted" size="sm">AI-Powered Resume Evaluation</Text>
              </div>
            </Link>
            <UserMenu />
          </div>
        </Container>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-8">
        <Container>{children}</Container>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <Container className="py-4">
          <Text variant="muted" size="sm" className="text-center">
            Powered by Claude AI
          </Text>
        </Container>
      </footer>
    </div>
  );
};
