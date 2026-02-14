/**
 * @fileoverview Application route definitions.
 *
 * Defines all routes for the CV Screening Agent application using React Router.
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
 * ```
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { CVPage, HistoryPage, CVDetailPage } from '@/features/cv';
import { NotificationSettingsPage } from '@/features/notification';
import {
  ProfilesPage,
  ProfileDetailPage,
  ProfileEditPage,
  ProfileCreatePage,
} from '@/features/profile';
import { SettingsPage } from '@/features/settings';
import { RouteErrorBoundary } from '@/shared/components/ui';
import { ProtectedRoute } from './guards';
import { RootLayout } from './RootLayout';

/**
 * Application router configuration.
 *
 * All routes are protected by authentication.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <RootLayout>
          <CVPage />
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
          <HistoryPage />
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
          <CVDetailPage />
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
          <ProfilesPage />
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
          <ProfileCreatePage />
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
          <ProfileDetailPage />
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
          <ProfileEditPage />
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
          <SettingsPage />
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
          <NotificationSettingsPage />
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
