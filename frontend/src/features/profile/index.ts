/**
 * @fileoverview Profile feature barrel export.
 *
 * Provides evaluation profile/template management functionality.
 *
 * @module features/profile
 *
 * @example
 * ```tsx
 * import { ProfilesPage, useProfiles } from '@/features/profile';
 * ```
 */

// Pages
export { ProfilesPage } from './pages/ProfilesPage';
export { ProfileDetailPage } from './pages/ProfileDetailPage';
export { ProfileEditPage } from './pages/ProfileEditPage';
export { ProfileCreatePage } from './pages/ProfileCreatePage';

// Hooks
export * from './hooks/useProfiles';

// API
export * from './api/profileApi';
