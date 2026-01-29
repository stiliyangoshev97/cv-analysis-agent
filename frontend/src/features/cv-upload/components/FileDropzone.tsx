import { useCallback, useState, type DragEvent, type ChangeEvent } from 'react';
import { clsx } from 'clsx';

interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  accept?: string;
}

export const FileDropzone = ({ onFileSelect, disabled = false, accept = '.pdf' }: FileDropzoneProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        onFileSelect(file);
      }
    }
  }, [disabled, onFileSelect]);

  const handleFileInput = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
    e.target.value = '';
  }, [onFileSelect]);

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={clsx(
        'relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200',
        isDragging && !disabled && 'border-blue-500 bg-blue-50',
        !isDragging && !disabled && 'border-gray-300 hover:border-gray-400 hover:bg-gray-50',
        disabled && 'border-gray-200 bg-gray-50 cursor-not-allowed opacity-60'
      )}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleFileInput}
        disabled={disabled}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
      />
      
      <div className="flex flex-col items-center gap-3">
        <div className={clsx(
          'w-14 h-14 rounded-full flex items-center justify-center',
          isDragging ? 'bg-blue-100' : 'bg-gray-100'
        )}>
          <svg
            className={clsx('w-7 h-7', isDragging ? 'text-blue-600' : 'text-gray-500')}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
        
        <div>
          <p className="text-base font-medium text-gray-700">
            {isDragging ? 'Drop your CV here' : 'Drag & drop your CV'}
          </p>
          <p className="mt-1 text-sm text-gray-500">
            or click to browse • PDF files only
          </p>
        </div>
      </div>
    </div>
  );
};
