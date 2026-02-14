/**
 * @fileoverview CV feature module.
 *
 * Provides CV upload and AI evaluation functionality.
 *
 * @module features/cv
 *
 * @example
 * ```typescript
 * import { CVPage, HistoryPage, CVDetailPage, useUploadCV, useDeleteCV, uploadCV } from '@/features/cv';
 * ```
 */

// Pages
export { CVPage, HistoryPage, CVDetailPage } from './pages';

// Components
export {
  FileDropzone,
  UploadProgress,
  Scorecard,
  ScoreRing,
  CriteriaItem,
} from './components';

// Hooks
export { useUploadCV, useCVList, useDeleteCV, useCV } from './hooks';

// API
export { uploadCV, checkHealth, deleteCV, getCV } from './api';
export type { CVDetailResponse } from './api';
