/**
 * @fileoverview CV feature module.
 *
 * Provides CV upload and AI evaluation functionality.
 *
 * @module features/cv
 *
 * @example
 * ```typescript
 * import { CVPage, HistoryPage, useUploadCV, uploadCV } from '@/features/cv';
 * ```
 */

// Pages
export { CVPage, HistoryPage } from './pages';

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
export { useCVList } from './hooks/useCVList';

// API
export { uploadCV, checkHealth } from './api';
