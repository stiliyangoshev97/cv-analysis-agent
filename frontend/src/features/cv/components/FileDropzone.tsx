/**
 * @fileoverview FileDropzone Component
 *
 * Drag-and-drop file upload zone for CV documents (PDF/DOCX).
 * Provides visual feedback during drag operations and validates file types.
 *
 * @module features/cv/components/FileDropzone
 *
 * FEATURES:
 * - Drag and drop support with visual feedback
 * - Click to browse fallback
 * - PDF and DOCX file type validation
 * - Single file limit enforcement
 * - Disabled state for upload-in-progress
 * - Error callbacks for validation failures
 *
 * @example
 * ```tsx
 * <FileDropzone
 *   onFileSelect={(file) => handleUpload(file)}
 *   onError={(msg) => setError(msg)}
 *   disabled={isUploading}
 * />
 * ```
 */

import { useCallback, useState, type DragEvent, type ChangeEvent } from 'react';
import { cn } from '@/shared/utils';

/** Allowed MIME types for CV uploads */
const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
  'application/msword', // .doc
];

/** Allowed file extensions for CV uploads */
const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc'];

/**
 * Check if a file is a valid CV document (PDF or DOCX).
 */
const isValidCVFile = (file: File): boolean => {
  // Check MIME type
  if (ALLOWED_MIME_TYPES.includes(file.type)) {
    return true;
  }
  
  // Fallback: check file extension (some browsers may not set MIME type correctly)
  const filename = file.name.toLowerCase();
  return ALLOWED_EXTENSIONS.some(ext => filename.endsWith(ext));
};

/**
 * FileDropzone component props.
 */
interface FileDropzoneProps {
  /** Callback when valid files are selected */
  onFileSelect: (file: File) => void;
  /** Callback when multiple files are selected (batch mode) */
  onFilesSelect?: (files: File[]) => void;
  /** Callback for validation errors */
  onError?: (message: string) => void;
  /** Disable the dropzone (e.g., during upload) */
  disabled?: boolean;
  /** Accepted file types (default: PDF and DOCX) */
  accept?: string;
  /** Allow multiple files (default: false) */
  multiple?: boolean;
  /** Maximum number of files allowed (default: 10) */
  maxFiles?: number;
}

/**
 * FileDropzone Component
 *
 * A drag-and-drop zone for uploading PDF files.
 * Validates file type and count before calling onFileSelect.
 *
 * @param props - Component props
 * @returns File upload dropzone element
 */
export const FileDropzone = ({
  onFileSelect,
  onFilesSelect,
  onError,
  disabled = false,
  accept = '.pdf,.docx,.doc,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword',
  multiple = false,
  maxFiles = 10,
}: FileDropzoneProps) => {
  const [isDragging, setIsDragging] = useState(false);

  /**
   * Validate and process files.
   */
  const processFiles = useCallback((fileList: FileList) => {
    const files = Array.from(fileList);
    
    // Filter for valid CV files (PDF and DOCX only)
    const validFiles = files.filter(isValidCVFile);
    const invalidCount = files.length - validFiles.length;
    
    if (invalidCount > 0) {
      onError?.(`${invalidCount} file(s) skipped. Only PDF and DOCX files are accepted.`);
    }
    
    if (validFiles.length === 0) {
      onError?.('No valid files found. Please upload PDF or DOCX files only.');
      return;
    }

    if (multiple) {
      // Batch mode
      if (validFiles.length > maxFiles) {
        onError?.(`Maximum ${maxFiles} files allowed. Only the first ${maxFiles} will be added.`);
        onFilesSelect?.(validFiles.slice(0, maxFiles));
      } else {
        onFilesSelect?.(validFiles);
      }
    } else {
      // Single file mode
      if (files.length > 1) {
        onError?.('Only 1 file is allowed. Please upload a single CV.');
        return;
      }
      if (validFiles.length === 1) {
        onFileSelect(validFiles[0]);
      }
    }
  }, [multiple, maxFiles, onFileSelect, onFilesSelect, onError]);

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

    processFiles(e.dataTransfer.files);
  }, [disabled, processFiles]);

  const handleFileInput = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
    e.target.value = '';
  }, [processFiles]);

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        'relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200',
        isDragging && !disabled && 'border-blue-500 bg-blue-50 dark:bg-blue-900/20',
        !isDragging && !disabled && 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800/50',
        disabled && 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 cursor-not-allowed opacity-60'
      )}
    >
      <input
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileInput}
        disabled={disabled}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
      />
      
      <div className="flex flex-col items-center gap-3">
        <div className={cn(
          'w-14 h-14 rounded-full flex items-center justify-center',
          isDragging ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-gray-100 dark:bg-gray-700'
        )}>
          <svg
            className={cn('w-7 h-7', isDragging ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400')}
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
          <p className="text-base font-medium text-gray-700 dark:text-gray-200">
            {isDragging ? 'Drop your CV(s) here' : multiple ? 'Drag & drop your CVs' : 'Drag & drop your CV'}
          </p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            or click to browse • PDF & DOCX only {multiple && `• Max ${maxFiles} files`}
          </p>
        </div>
      </div>
    </div>
  );
};
