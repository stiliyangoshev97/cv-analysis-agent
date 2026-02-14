/**
 * @fileoverview Compare CVs Modal Component
 *
 * Modal for selecting and comparing 2-5 CVs with AI analysis.
 * Shows candidate selection, comparison question input, and results.
 *
 * @module features/chat/components/CompareCVsModal
 */

import { useState } from 'react';
import { Button, Text, Heading, Spinner, Badge, Input } from '@/shared/components';
import { useCVList } from '@/features/cv/hooks';
import { useCompareCVs } from '../hooks';
import type { CVSummary, CompareResponse } from '@/shared/types';

interface CompareCVsModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback to close the modal */
  onClose: () => void;
}

/**
 * Compare CVs Modal Component
 *
 * Allows users to select 2-5 CVs and get AI-powered comparison analysis.
 *
 * @example
 * ```tsx
 * <CompareCVsModal
 *   isOpen={showCompare}
 *   onClose={() => setShowCompare(false)}
 * />
 * ```
 */
export const CompareCVsModal = ({ isOpen, onClose }: CompareCVsModalProps) => {
  const [selectedCVs, setSelectedCVs] = useState<string[]>([]);
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<CompareResponse | null>(null);

  const { data: cvList, isLoading: isLoadingCVs } = useCVList();
  const { mutate: compare, isPending: isComparing, reset } = useCompareCVs();

  const handleToggleCV = (cvId: string) => {
    setSelectedCVs((prev) => {
      if (prev.includes(cvId)) {
        return prev.filter((id) => id !== cvId);
      }
      if (prev.length >= 5) {
        return prev; // Max 5 CVs
      }
      return [...prev, cvId];
    });
  };

  const handleCompare = () => {
    if (selectedCVs.length < 2) return;

    compare(
      {
        cvIds: selectedCVs,
        question: question.trim() || 'Compare these candidates overall',
      },
      {
        onSuccess: (data) => {
          setResult(data);
        },
      }
    );
  };

  const handleReset = () => {
    setSelectedCVs([]);
    setQuestion('');
    setResult(null);
    reset();
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  if (!isOpen) return null;

  // Get CV details for selected CVs
  const getCV = (cvId: string): CVSummary | undefined => {
    return cvList?.cvs.find((cv) => cv.id === cvId);
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={handleClose}
      >
        {/* Modal */}
        <div
          className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[85vh] overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div>
              <Heading level={4}>Compare Candidates</Heading>
              <Text size="sm" color="muted">
                Select 2-5 CVs to compare with AI analysis
              </Text>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {result ? (
              /* Results View */
              <div className="space-y-6">
                {/* Selected CVs Summary */}
                <div>
                  <Text weight="medium" className="mb-2">Compared Candidates</Text>
                  <div className="flex flex-wrap gap-2">
                    {result.cv_ids.map((cvId) => {
                      const cv = getCV(cvId);
                      return (
                        <Badge key={cvId} variant="info" size="md">
                          {cv?.candidate_name || cv?.filename || cvId.slice(0, 8)}
                        </Badge>
                      );
                    })}
                  </div>
                </div>

                {/* Comparison Analysis */}
                <div>
                  <Text weight="medium" className="mb-2">AI Analysis</Text>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <Text size="sm" className="whitespace-pre-wrap leading-relaxed">
                      {result.comparison}
                    </Text>
                  </div>
                </div>

                {/* Ranking */}
                {result.ranking && result.ranking.length > 0 && (
                  <div>
                    <Text weight="medium" className="mb-3">Candidate Ranking</Text>
                    <div className="space-y-3">
                      {result.ranking.map((item) => {
                        const cv = getCV(item.cv_id);
                        return (
                          <div
                            key={item.cv_id}
                            className={`flex items-start gap-4 p-4 rounded-lg border ${
                              item.rank === 1
                                ? 'bg-green-50 border-green-200'
                                : item.rank === 2
                                ? 'bg-blue-50 border-blue-200'
                                : 'bg-gray-50 border-gray-200'
                            }`}
                          >
                            <div
                              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                                item.rank === 1
                                  ? 'bg-green-500'
                                  : item.rank === 2
                                  ? 'bg-blue-500'
                                  : 'bg-gray-400'
                              }`}
                            >
                              {item.rank}
                            </div>
                            <div className="flex-1 min-w-0">
                              <Text weight="medium">
                                {cv?.candidate_name || cv?.filename || 'Unknown'}
                              </Text>
                              {cv?.score !== null && cv?.score !== undefined && (
                                <Badge
                                  variant={cv.evaluation_status === 'pass' ? 'success' : 'error'}
                                  size="sm"
                                  className="ml-2"
                                >
                                  Score: {cv.score}%
                                </Badge>
                              )}
                              <Text size="sm" color="muted" className="mt-1">
                                {item.reason}
                              </Text>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Compare Again Button */}
                <div className="flex justify-center pt-4">
                  <Button variant="outline" onClick={handleReset}>
                    Compare Different CVs
                  </Button>
                </div>
              </div>
            ) : (
              /* Selection View */
              <div className="space-y-6">
                {/* Comparison Question */}
                <div>
                  <Text weight="medium" className="mb-2">Comparison Focus (Optional)</Text>
                  <Input
                    placeholder="e.g., Compare their fintech experience"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="w-full"
                  />
                  <Text size="xs" color="muted" className="mt-1">
                    Leave empty for general comparison
                  </Text>
                </div>

                {/* CV Selection */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Text weight="medium">Select Candidates</Text>
                    <Badge variant={selectedCVs.length >= 2 ? 'success' : 'neutral'}>
                      {selectedCVs.length} / 5 selected
                    </Badge>
                  </div>

                  {isLoadingCVs ? (
                    <div className="flex items-center justify-center py-12">
                      <Spinner size="lg" />
                    </div>
                  ) : !cvList || cvList.cvs.length === 0 ? (
                    <div className="text-center py-12 bg-gray-50 rounded-lg">
                      <Text color="muted">No CVs found. Upload some CVs first!</Text>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[300px] overflow-y-auto">
                      {cvList.cvs.map((cv) => {
                        const isSelected = selectedCVs.includes(cv.id);
                        const isDisabled = !isSelected && selectedCVs.length >= 5;

                        return (
                          <button
                            key={cv.id}
                            onClick={() => handleToggleCV(cv.id)}
                            disabled={isDisabled}
                            className={`text-left p-4 rounded-lg border-2 transition-all ${
                              isSelected
                                ? 'border-blue-500 bg-blue-50'
                                : isDisabled
                                ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                                : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div
                                className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                                  isSelected
                                    ? 'bg-blue-500 border-blue-500'
                                    : 'border-gray-300'
                                }`}
                              >
                                {isSelected && (
                                  <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                  </svg>
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <Text weight="medium" className="truncate">
                                  {cv.candidate_name || 'Unknown Candidate'}
                                </Text>
                                <Text size="xs" color="muted" className="truncate">
                                  {cv.filename}
                                </Text>
                                <div className="flex items-center gap-2 mt-1">
                                  {cv.score !== null && cv.score !== undefined && (
                                    <Badge
                                      variant={cv.evaluation_status === 'pass' ? 'success' : 'error'}
                                      size="sm"
                                    >
                                      {cv.score}%
                                    </Badge>
                                  )}
                                  {cv.evaluation_status && (
                                    <Badge
                                      variant={cv.evaluation_status === 'pass' ? 'success' : 'error'}
                                      size="sm"
                                    >
                                      {cv.evaluation_status}
                                    </Badge>
                                  )}
                                </div>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          {!result && (
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-between">
              <Button variant="ghost" onClick={handleClose}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleCompare}
                disabled={selectedCVs.length < 2 || isComparing}
                isLoading={isComparing}
                className="gap-2"
              >
                {isComparing ? (
                  'Comparing...'
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Compare ({selectedCVs.length})
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};
