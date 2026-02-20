/**
 * @fileoverview Root layout component.
 *
 * Provides the main application layout with header and footer.
 * Uses shared Container and Text components for consistent styling.
 * Includes mobile-responsive hamburger menu for navigation.
 *
 * @module router/RootLayout
 */

import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { UserMenu } from '@/features/auth';
import { SetupBanner } from '@/features/settings';
import { Container, Text, Heading, ThemeToggle } from '@/shared/components/ui';
import { cn } from '@/shared/utils';

/** Navigation links configuration */
const navLinks = [
  { to: '/', label: 'Evaluate' },
  { to: '/history', label: 'History' },
  { to: '/profiles', label: 'Profiles' },
  { to: '/settings', label: 'Settings' },
];

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
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col transition-colors">
      {/* Setup Warning Banner (persists until configured) */}
      <SetupBanner />

      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <Container className="py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 sm:gap-8">
              {/* Mobile Menu Button */}
              <button
                type="button"
                className="md:hidden p-2 -ml-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                )}
              </button>

              <Link to="/" className="flex items-center gap-2 sm:gap-3 hover:opacity-80 transition-opacity">
                <div className="w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 dark:bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg
                    className="w-5 h-5 sm:w-6 sm:h-6 text-white"
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
                <div className="hidden sm:block">
                  <Heading level={4} className="text-lg sm:text-xl text-gray-900 dark:text-white">CV Screening Agent</Heading>
                  <Text variant="muted" size="sm" className="dark:text-gray-400 hidden lg:block">AI-Powered Resume Evaluation</Text>
                </div>
              </Link>

              {/* Desktop Navigation */}
              <nav className="hidden md:flex items-center gap-1">
                {navLinks.map((link) => {
                  const isActive = link.to === '/'
                    ? location.pathname === '/'
                    : location.pathname.startsWith(link.to);

                  return (
                    <Link
                      key={link.to}
                      to={link.to}
                      className={cn(
                        'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                          : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                      )}
                    >
                      {link.label}
                    </Link>
                  );
                })}
              </nav>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <ThemeToggle />
              <UserMenu />
            </div>
          </div>

          {/* Mobile Navigation Menu */}
          {mobileMenuOpen && (
            <nav className="md:hidden mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex flex-col gap-1">
                {navLinks.map((link) => {
                  const isActive = link.to === '/'
                    ? location.pathname === '/'
                    : location.pathname.startsWith(link.to);

                  return (
                    <Link
                      key={link.to}
                      to={link.to}
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        'px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                          : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                      )}
                    >
                      {link.label}
                    </Link>
                  );
                })}
              </div>
            </nav>
          )}
        </Container>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-4 sm:py-8">
        <Container>{children}</Container>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <Container className="py-4">
          <div className="flex items-center justify-center gap-4">
            <Link
              to="/settings/models"
              className="inline-link text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors leading-normal"
            >
              AI Models Guide
            </Link>
            <span className="text-gray-300 dark:text-gray-600">•</span>
            <span className="text-sm text-gray-500 dark:text-gray-400 leading-normal">
              © 2026 CV Screening Agent
            </span>
          </div>
        </Container>
      </footer>
    </div>
  );
};
