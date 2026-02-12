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
 * └── /                      [PROTECTED]  CV Upload/Evaluation page
 * ```
 *
 * ROUTE GUARDS:
 * - ProtectedRoute: Requires authentication
 *
 * @example
 * ```tsx
 * import { ProtectedRoute, RootLayout } from '@/router';
 * ```
 */

export { ProtectedRoute } from './guards';
export { RootLayout } from './RootLayout';
