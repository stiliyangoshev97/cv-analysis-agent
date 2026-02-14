/**
 * @fileoverview CVFileList Component
 *
 * Displays a list of staged CV files before scanning.
 * Allows users to review and remove files before confirming.
 *
 * @module features/cv/components/CVFileList
 */

import { Button, Text } from '@/shared/components/ui';
import { cn } from '@/shared/utils';

/**
 * Staged file with metadata.
 */
export interface StagedFile {
  /** Unique ID for the file */
  id: string;
  /** The actual file object */
  file: File;
  /** Current status */
  status: 'pending' | 'uploading' | 'success' | 'error';
  /** Upload progress (0-100) */
  progress?: number;
  /** Error message if failed */
  error?: string;
}

interface CVFileListProps {
  /** List of staged files */
  files: StagedFile[];
  /** Callback to remove a file */
  onRemove: (id: string) => void;
  /** Whether scanning is in progress */
  isScanning: boolean;
}

/**
 * Format file size in human-readable format.
 */
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

/**
 * CVFileList Component
 *
 * Shows a list of files staged for scanning with remove buttons.
 */
export const CVFileList = ({ files, onRemove, isScanning }: CVFileListProps) => {
  if (files.length === 0) return null;

  return (
    <div className="space-y-2">
      {files.map((stagedFile) => (
        <div
          key={stagedFile.id}
          className={cn(
            'flex items-center gap-3 p-3 rounded-lg border transition-colors',
            'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700',
            stagedFile.status === 'error' && 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20',
            stagedFile.status === 'success' && 'border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20'
          )}
        >
          {/* File Icon */}
          <div className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
            stagedFile.status === 'error' ? 'bg-red-100 dark:bg-red-900/30' :
            stagedFile.status === 'success' ? 'bg-green-100 dark:bg-green-900/30' :
            'bg-gray-100 dark:bg-gray-700'
          )}>
            <svg
              className={cn(
                'w-5 h-5',
                stagedFile.status === 'error' ? 'text-red-600 dark:text-red-400' :
                stagedFile.status === 'success' ? 'text-green-600 dark:text-green-400' :
                'text-gray-500 dark:text-gray-400'
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>

          {/* File Info */}
          <div className="flex-1 min-w-0">
            <Text className="font-medium truncate dark:text-gray-100">
              {stagedFile.file.name}
            </Text>
            <Text size="xs" variant="muted">
              {formatFileSize(stagedFile.file.size)}
              {stagedFile.status === 'uploading' && stagedFile.progress !== undefined && (
                <span className="ml-2">• {stagedFile.progress}%</span>
              )}
              {stagedFile.status === 'success' && (
                <span className="ml-2 text-green-600 dark:text-green-400">• Completed</span>
              )}
              {stagedFile.status === 'error' && stagedFile.error && (
                <span className="ml-2 text-red-600 dark:text-red-400">• {stagedFile.error}</span>
              )}
            </Text>
          </div>

          {/* Progress Bar (when uploading) */}
          {stagedFile.status === 'uploading' && stagedFile.progress !== undefined && (
            <div className="w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 dark:bg-blue-500 rounded-full transition-all duration-300"
                style={{ width: `${stagedFile.progress}%` }}
              />
            </div>
          )}

          {/* Status Icons */}
          {stagedFile.status === 'success' && (
            <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
          {stagedFile.status === 'error' && (
            <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )}

          {/* Remove Button (only when pending) */}
          {stagedFile.status === 'pending' && !isScanning && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onRemove(stagedFile.id)}
              className="text-gray-400 hover:text-red-600 dark:hover:text-red-400"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          )}
        </div>
      ))}
    </div>
  );
};
