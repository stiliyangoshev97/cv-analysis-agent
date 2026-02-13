/**
 * @fileoverview Application router configuration.
 *
 * Defines all routes for the CV Screening Agent application.
 *
 * @module router
 *
 * ROUTE STRUCTURE:
 * ```
 * / (RootLayout)
 * └── /                           [PROTECTED]  CV Upload/Evaluation page
 * └── /settings/notifications     [PROTECTED]  Notification Settings page
 * ```
 *
 * ROUTE GUARDS:
 * - ProtectedRoute: Requires authentication
 *
 * @example
 * ```tsx
 * import { router } from '@/router';
 * import { RouterProvider } from 'react-router-dom';
 * 
 * <RouterProvider router={router} />
 * ```
 */

export { ProtectedRoute } from './guards';
export { RootLayout } from './RootLayout';
export { router } from './routes';
