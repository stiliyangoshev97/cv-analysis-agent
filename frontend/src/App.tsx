
import { useState, useCallback } from 'react';
import { FileDropzone, UploadProgress, useUploadCV } from './features/cv-upload';
import { Scorecard } from './features/scorecard';
import type { CVResult } from './types';

const App = () => {
  const [result, setResult] = useState<CVResult | null>(null);
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  const { upload, isUploading, progress, error, reset } = useUploadCV();

  const handleFileSelect = useCallback((file: File) => {
    setCurrentFile(file.name);
    setResult(null); // Clear previous result
    
    upload(file, {
      onSuccess: (data) => {
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

  const handleDismiss = useCallback(() => {
    setResult(null);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">CV Screening Agent</h1>
              <p className="text-sm text-gray-500">AI-Powered Resume Evaluation</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Upload Section */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload CV</h2>
          
          {isUploading && progress && currentFile ? (
            <UploadProgress filename={currentFile} progress={progress} />
          ) : (
            <FileDropzone onFileSelect={handleFileSelect} disabled={isUploading} />
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">
                <span className="font-medium">Error:</span> {error.message}
              </p>
            </div>
          )}
        </section>

        {/* Results Section */}
        {result && (
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Result</h2>
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
            <h3 className="text-lg font-medium text-gray-900 mb-1">No CVs evaluated yet</h3>
            <p className="text-sm text-gray-500">Upload a PDF CV to get started</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-auto">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <p className="text-sm text-gray-500 text-center">
            Powered by Claude AI
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;