/**
 * @fileoverview CV feature module.
 *
 * Provides CV upload and AI evaluation functionality.
 *
 * @module features/cv
 *
 * @example
 * ```typescript
 * import { CVPage, useUploadCV, uploadCV } from '@/features/cv';
 * ```
 */

// Pages
export { CVPage } from './pages';

// Components
export {
  FileDropzone,
  UploadProgress,
  Scorecard,
  ScoreRing,
  CriteriaItem,
} from './components';

// Hooks
export { useUploadCV } from './hooks';

// API
export { uploadCV, checkHealth } from './api';
