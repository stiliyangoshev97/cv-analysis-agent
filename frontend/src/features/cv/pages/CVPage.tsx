/**
 * @fileoverview Main CV screening page.
 *
 * Allows users to upload multiple CVs, review them, and then scan with AI.
 * Features batch upload (up to 10 CVs) with confirmation before scanning.
 *
 * @module features/cv/pages/CVPage
 */

import { useState, useCallback } from 'react';
import { FileDropzone, CVFileList, Scorecard, type StagedFile } from '../components';
import { useUploadCV } from '../hooks';
import { SetupRequiredScreen, useSetupStatus } from '@/features/settings';
import { CompareCVsModal } from '@/features/chat';
import { Heading, Text, Spinner, Button, Card, toast } from '@/shared/components/ui';
import type { CVResult, UploadResponse } from '@/shared/types';

/** Maximum number of CVs that can be uploaded at once */
const MAX_FILES = 10;

/**
 * CV screening page component.
 *
 * Features:
 * - Batch PDF upload with drag-and-drop (up to 10 files)
 * - Review staged files before scanning
 * - "Scan CVs" button to confirm and start AI evaluation
 * - Results displayed in scorecards
 * - Blocks upload if setup is incomplete
 *
 * @returns CV upload and evaluation page
 */
export const CVPage = () => {
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([]);
  const [results, setResults] = useState<CVResult[]>([]);
  const [fileError, setFileError] = useState<string | null>(null);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const { upload } = useUploadCV();
  
  // Check if setup is complete
  const { data: setupStatus, isLoading: isLoadingSetup } = useSetupStatus();

  /**
   * Handle multiple files selected (batch mode).
   */
  const handleFilesSelect = useCallback((files: File[]) => {
    setFileError(null);
    
    // Check if adding these would exceed the limit
    const currentCount = stagedFiles.length;
    const availableSlots = MAX_FILES - currentCount;
    
    if (availableSlots <= 0) {
      setFileError(`Maximum ${MAX_FILES} files allowed. Remove some files to add more.`);
      return;
    }
    
    // Filter out duplicates (by name)
    const existingNames = new Set(stagedFiles.map(sf => sf.file.name));
    const newFiles = files.filter(f => !existingNames.has(f.name));
    
    if (newFiles.length < files.length) {
      const skipped = files.length - newFiles.length;
      toast.info(`${skipped} duplicate file(s) skipped`);
    }
    
    // Add only up to available slots
    const filesToAdd = newFiles.slice(0, availableSlots);
    
    if (filesToAdd.length < newFiles.length) {
      toast.warning(`Only ${filesToAdd.length} of ${newFiles.length} files added (max ${MAX_FILES})`);
    }
    
    // Create staged file entries
    const newStagedFiles: StagedFile[] = filesToAdd.map(file => ({
      id: crypto.randomUUID(),
      file,
      status: 'pending',
    }));
    
    setStagedFiles(prev => [...prev, ...newStagedFiles]);
  }, [stagedFiles]);

  /**
   * Remove a staged file.
   */
  const handleRemoveFile = useCallback((id: string) => {
    setStagedFiles(prev => prev.filter(sf => sf.id !== id));
  }, []);

  /**
   * Clear all staged files.
   */
  const handleClearAll = useCallback(() => {
    setStagedFiles([]);
    setFileError(null);
  }, []);

  /**
   * Start scanning all staged CVs.
   */
  const handleScanCVs = useCallback(async () => {
    if (stagedFiles.length === 0) return;
    
    setIsScanning(true);
    setFileError(null);
    
    // Process files sequentially
    for (const stagedFile of stagedFiles) {
      // Update status to uploading
      setStagedFiles(prev => prev.map(sf => 
        sf.id === stagedFile.id ? { ...sf, status: 'uploading', progress: 0 } : sf
      ));
      
      try {
        // Upload and evaluate
        const data = await new Promise<UploadResponse>((resolve, reject) => {
          upload(stagedFile.file, {
            onSuccess: (response: UploadResponse) => resolve(response),
            onError: (error: Error) => reject(error),
          });
        });
        
        if (data.success && data.evaluation) {
          // Add to results
          const result: CVResult = {
            id: crypto.randomUUID(),
            filename: stagedFile.file.name,
            evaluation: data.evaluation,
            uploadedAt: new Date(),
          };
          setResults(prev => [...prev, result]);
          
          // Update status to success
          setStagedFiles(prev => prev.map(sf => 
            sf.id === stagedFile.id ? { ...sf, status: 'success', progress: 100 } : sf
          ));
        } else {
          throw new Error('Evaluation failed');
        }
      } catch (error) {
        // Update status to error
        const errorMessage = error instanceof Error ? error.message : 'Upload failed';
        setStagedFiles(prev => prev.map(sf => 
          sf.id === stagedFile.id ? { ...sf, status: 'error', error: errorMessage } : sf
        ));
      }
    }
    
    setIsScanning(false);
    
    // Show completion toast
    const successCount = stagedFiles.filter(sf => 
      document.querySelector(`[data-file-id="${sf.id}"]`)?.getAttribute('data-status') === 'success'
    ).length || stagedFiles.length;
    toast.success(`Scanning complete`, `${successCount} CV(s) evaluated`);
  }, [stagedFiles, upload]);

  /**
   * Dismiss a scorecard result.
   */
  const handleDismissResult = useCallback((id: string) => {
    setResults(prev => prev.filter(r => r.id !== id));
  }, []);

  /**
   * Handle file validation errors.
   */
  const handleFileError = useCallback((message: string) => {
    setFileError(message);
  }, []);

  // Count pending files
  const pendingCount = stagedFiles.filter(sf => sf.status === 'pending').length;
  const hasCompleted = stagedFiles.some(sf => sf.status === 'success' || sf.status === 'error');

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
      {/* Page Header with Compare Button */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Heading level={1} className="text-2xl">CV Screening</Heading>
          <Text variant="muted">Upload and evaluate candidate CVs with AI</Text>
        </div>
        <Button
          variant="outline"
          onClick={() => setShowCompareModal(true)}
          className="gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Compare CVs
        </Button>
      </div>

      {/* Upload Section */}
      <section className="mb-8">
        <Card>
          <div className="mb-4">
            <Heading level={2} className="text-lg">Upload CVs</Heading>
            <Text variant="muted" size="sm">
              Add up to {MAX_FILES} CVs, review them, then click "Scan CVs" to start evaluation
            </Text>
          </div>

          {/* Dropzone */}
          <FileDropzone
            onFileSelect={() => {}} // Not used in batch mode
            onFilesSelect={handleFilesSelect}
            onError={handleFileError}
            disabled={isScanning || stagedFiles.length >= MAX_FILES}
            multiple
            maxFiles={MAX_FILES - stagedFiles.length}
          />

          {/* Error Message */}
          {fileError && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <Text size="sm" variant="error">
                {fileError}
              </Text>
            </div>
          )}

          {/* Staged Files List */}
          {stagedFiles.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-3">
                <Text weight="medium" className="dark:text-gray-100">
                  {stagedFiles.length} CV{stagedFiles.length !== 1 ? 's' : ''} staged
                </Text>
                {!isScanning && !hasCompleted && (
                  <Button variant="ghost" size="sm" onClick={handleClearAll}>
                    Clear All
                  </Button>
                )}
              </div>
              
              <CVFileList
                files={stagedFiles}
                onRemove={handleRemoveFile}
                isScanning={isScanning}
              />

              {/* Action Buttons */}
              <div className="mt-6 flex items-center gap-3">
                {pendingCount > 0 && !hasCompleted && (
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={handleScanCVs}
                    isLoading={isScanning}
                    disabled={isScanning}
                    className="gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    Scan {pendingCount} CV{pendingCount !== 1 ? 's' : ''}
                  </Button>
                )}
                {hasCompleted && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      setStagedFiles([]);
                      setFileError(null);
                    }}
                  >
                    Upload More CVs
                  </Button>
                )}
              </div>
            </div>
          )}
        </Card>
      </section>

      {/* Results Section */}
      {results.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <Heading level={2} className="text-lg">
              Results ({results.length})
            </Heading>
            {results.length > 1 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setResults([])}
              >
                Clear All Results
              </Button>
            )}
          </div>
          <div className="space-y-4">
            {results.map(result => (
              <Scorecard
                key={result.id}
                result={result}
                onDismiss={() => handleDismissResult(result.id)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Empty State */}
      {results.length === 0 && stagedFiles.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <Heading level={3} className="text-lg mb-1">No CVs evaluated yet</Heading>
          <Text size="sm" variant="muted">Upload PDF CVs to get started</Text>
        </div>
      )}

      {/* Compare CVs Modal */}
      <CompareCVsModal
        isOpen={showCompareModal}
        onClose={() => setShowCompareModal(false)}
      />
    </>
  );
};
