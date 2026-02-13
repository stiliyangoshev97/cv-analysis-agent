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
 * /settings/notifications     [PROTECTED] Notification settings page
 * ```
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { CVPage } from '@/features/cv';
import { NotificationSettingsPage } from '@/features/notification';
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
  },
  {
    // Catch-all redirect to home
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
