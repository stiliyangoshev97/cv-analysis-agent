/**
 * @fileoverview Application route definitions.
 *
 * Defines all routes for the CV Screening Agent application using React Router.
 * Uses React.lazy() for code-splitting and improved initial load performance.
 *
 * @module router/routes
 *
 * ROUTE STRUCTURE:
 * ```
 * /                           [PROTECTED] CV Upload/Evaluation page
 * /history                    [PROTECTED] CV Evaluation history
 * /history/:id                [PROTECTED] CV Detail view
 * /profiles                   [PROTECTED] Evaluation profiles list
 * /profiles/new               [PROTECTED] Create new profile
 * /profiles/:id               [PROTECTED] View profile details
 * /profiles/:id/edit          [PROTECTED] Edit profile
 * /settings                   [PROTECTED] API Keys & LLM Preferences
 * /settings/notifications     [PROTECTED] Notification settings page
 * /settings/models            [PROTECTED] LLM Models FAQ page
 * ```
 *
 * PERFORMANCE:
 * - All page components are lazy-loaded for code-splitting
 * - Each route chunk is loaded on-demand when navigating
 * - PageLoader provides visual feedback during chunk loading
 */

import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { PageLoader, RouteErrorBoundary } from '@/shared/components/ui';
import { ProtectedRoute } from './guards';
import { RootLayout } from './RootLayout';

// Lazy-loaded page components for code-splitting
const CVPage = lazy(() => import('@/features/cv/pages/CVPage').then(m => ({ default: m.CVPage })));
const HistoryPage = lazy(() => import('@/features/cv/pages/HistoryPage').then(m => ({ default: m.HistoryPage })));
const CVDetailPage = lazy(() => import('@/features/cv/pages/CVDetailPage').then(m => ({ default: m.CVDetailPage })));

const ProfilesPage = lazy(() => import('@/features/profile/pages/ProfilesPage').then(m => ({ default: m.ProfilesPage })));
const ProfileDetailPage = lazy(() => import('@/features/profile/pages/ProfileDetailPage').then(m => ({ default: m.ProfileDetailPage })));
const ProfileEditPage = lazy(() => import('@/features/profile/pages/ProfileEditPage').then(m => ({ default: m.ProfileEditPage })));
const ProfileCreatePage = lazy(() => import('@/features/profile/pages/ProfileCreatePage').then(m => ({ default: m.ProfileCreatePage })));

const SettingsPage = lazy(() => import('@/features/settings/pages/SettingsPage').then(m => ({ default: m.SettingsPage })));
const LlmFaqPage = lazy(() => import('@/features/settings/pages/LlmFaqPage').then(m => ({ default: m.LlmFaqPage })));

const NotificationSettingsPage = lazy(() => import('@/features/notification/pages/NotificationSettingsPage').then(m => ({ default: m.NotificationSettingsPage })));
const NotificationHistoryPage = lazy(() => import('@/features/notification/pages/NotificationHistoryPage').then(m => ({ default: m.NotificationHistoryPage })));

/**
 * Wraps a lazy-loaded component with Suspense for loading state.
 */
const withSuspense = (Component: React.LazyExoticComponent<React.ComponentType>) => (
  <Suspense fallback={<PageLoader />}>
    <Component />
  </Suspense>
);

/**
 * Application router configuration.
 *
 * All routes are protected by authentication.
 * Pages are lazy-loaded for optimal bundle splitting.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(CVPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/history',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(HistoryPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/history/:id',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(CVDetailPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/profiles',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(ProfilesPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/profiles/new',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(ProfileCreatePage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/profiles/:id',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(ProfileDetailPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/profiles/:id/edit',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(ProfileEditPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/settings',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(SettingsPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/settings/notifications',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(NotificationSettingsPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/settings/notifications/history',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(NotificationHistoryPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    path: '/settings/models',
    element: (
      <ProtectedRoute>
        <RootLayout>
          {withSuspense(LlmFaqPage)}
        </RootLayout>
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorBoundary />,
  },
  {
    // Catch-all redirect to home
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
