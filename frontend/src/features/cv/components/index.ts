/**
 * @fileoverview Barrel export for CV feature components.
 * @module features/cv/components
 */

// Upload components
export { FileDropzone } from './FileDropzone';
export { UploadProgress } from './UploadProgress';
export { CVFileList, type StagedFile } from './CVFileList';
export { TemplateSelector } from './TemplateSelector';

// Scorecard components
export { Scorecard } from './Scorecard';
export { ScoreRing } from './ScoreRing';
export { CriteriaItem } from './CriteriaItem';

// Similarity & Search components
export { SimilarCVsModal } from './SimilarCVsModal';
export { RankingBadge, RankingInline } from './RankingBadge';
export { SemanticSearchBar, SearchResults } from './SemanticSearchBar';
export { CVComparisonModal } from './CVComparisonModal';
