/**
 * @fileoverview UploadProgress Component
 *
 * Displays file upload progress with filename, size, and progress bar.
 * Shows during active CV uploads.
 *
 * @module features/cv/components/UploadProgress
 *
 * FEATURES:
 * - Filename display with PDF icon
 * - Upload size progress (loaded/total)
 * - Animated progress bar
 * - Spinning loader indicator
 * - Percentage display
 *
 * @example
 * ```tsx
 * <UploadProgress
 *   filename="resume.pdf"
 *   progress={{
 *     loaded: 512000,
 *     total: 1024000,
 *     percentage: 50,
 *   }}
 * />
 * ```
 */

import { Card, ProgressBar, Spinner, Text } from '@/shared/components/ui';
import type { UploadProgress as UploadProgressType } from '@/shared/types';

/**
 * UploadProgress component props.
 */
interface UploadProgressProps {
  /** Name of the file being uploaded */
  filename: string;
  /** Upload progress data */
  progress: UploadProgressType;
}

/**
 * Format bytes to human-readable size.
 *
 * @param bytes - Size in bytes
 * @returns Formatted size string (e.g., "1.5 MB")
 */
const formatSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

/**
 * UploadProgress Component
 *
 * Shows file upload progress with visual indicators.
 *
 * @param props - Component props
 * @returns Upload progress element
 */
export const UploadProgress = ({ filename, progress }: UploadProgressProps) => {
  return (
    <Card padding="md">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <Text weight="medium" size="sm" className="truncate">{filename}</Text>
          <Text variant="muted" size="xs">
            {formatSize(progress.loaded)} of {formatSize(progress.total)}
          </Text>
        </div>
        <div className="flex items-center gap-2">
          <Spinner size="sm" className="text-blue-600" />
          <Text weight="medium" size="sm" className="text-blue-600">
            {progress.percentage}%
          </Text>
        </div>
      </div>
      <ProgressBar value={progress.percentage} />
    </Card>
  );
};
