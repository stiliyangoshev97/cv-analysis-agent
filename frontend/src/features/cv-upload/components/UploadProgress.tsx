import { ProgressBar } from '../../../components/ui';
import type { UploadProgress as UploadProgressType } from '../../../types';

interface UploadProgressProps {
  filename: string;
  progress: UploadProgressType;
}

export const UploadProgress = ({ filename, progress }: UploadProgressProps) => {
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">{filename}</p>
          <p className="text-xs text-gray-500">
            {formatSize(progress.loaded)} of {formatSize(progress.total)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-blue-600">{progress.percentage}%</span>
        </div>
      </div>
      <ProgressBar value={progress.percentage} />
    </div>
  );
};
