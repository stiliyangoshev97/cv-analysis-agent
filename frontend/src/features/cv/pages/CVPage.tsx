/**
 * @fileoverview Main CV screening page.
 *
 * Allows users to upload a CV and view AI evaluation results.
 *
 * @module features/cv/pages/CVPage
 */

import { useState, useCallback } from 'react';
import { FileDropzone, UploadProgress, Scorecard } from '../components';
import { useUploadCV } from '../hooks';
import { SetupRequiredScreen, useSetupStatus } from '@/features/settings';
import { Heading, Text, Spinner } from '@/shared/components/ui';
import type { CVResult, UploadResponse } from '@/shared/types';

/**
 * CV screening page component.
 *
 * Features:
 * - PDF upload with drag-and-drop
 * - Upload progress tracking
 * - AI evaluation scorecard display
 * - Blocks upload if setup is incomplete
 *
 * @returns CV upload and evaluation page
 */
export const CVPage = () => {
  const [result, setResult] = useState<CVResult | null>(null);
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const { upload, isUploading, progress, error, reset } = useUploadCV();
  
  // Check if setup is complete
  const { data: setupStatus, isLoading: isLoadingSetup } = useSetupStatus();

  /**
   * Handle file selection and start upload.
   */
  const handleFileSelect = useCallback((file: File) => {
    setFileError(null);
    setCurrentFile(file.name);
    setResult(null);

    upload(file, {
      onSuccess: (data: UploadResponse) => {
        if (data.success && data.evaluation) {
          setResult({
            id: crypto.randomUUID(),
            filename: file.name,
            evaluation: data.evaluation,
            uploadedAt: new Date(),
          });
        }
        setCurrentFile(null);
        reset();
      },
      onError: () => {
        setCurrentFile(null);
      },
    });
  }, [upload, reset]);

  /**
   * Handle file validation errors.
   */
  const handleFileError = useCallback((message: string) => {
    setFileError(message);
  }, []);

  /**
   * Dismiss the scorecard result.
   */
  const handleDismiss = useCallback(() => {
    setResult(null);
  }, []);

  // Show loading while checking setup status
  if (isLoadingSetup) {
    return (
      <div className="flex items-center justify-center py-16">
        <Spinner size="lg" />
      </div>
    );
  }

  // Block access if setup is not complete
  if (setupStatus && !setupStatus.is_complete) {
    return <SetupRequiredScreen />;
  }

  return (
    <>
      {/* Upload Section */}
      <section className="mb-8">
        <Heading level={2} className="text-lg mb-4">Upload CV</Heading>

        {isUploading && progress && currentFile ? (
          <UploadProgress filename={currentFile} progress={progress} />
        ) : (
          <FileDropzone
            onFileSelect={handleFileSelect}
            onError={handleFileError}
            disabled={isUploading}
          />
        )}

        {(error || fileError) && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <Text size="sm" color="error">
              <span className="font-medium">Error:</span> {fileError || error?.message}
            </Text>
          </div>
        )}
      </section>

      {/* Results Section */}
      {result && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <Heading level={2} className="text-lg">Result</Heading>
          </div>
          <Scorecard result={result} onDismiss={handleDismiss} />
        </section>
      )}

      {/* Empty State */}
      {!result && !isUploading && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <Heading level={3} className="text-lg mb-1">No CVs evaluated yet</Heading>
          <Text size="sm" color="muted">Upload a PDF CV to get started</Text>
        </div>
      )}
    </>
  );
};
