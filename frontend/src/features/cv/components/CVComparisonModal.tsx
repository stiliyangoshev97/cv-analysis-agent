/**
 * @fileoverview CV Comparison Modal component.
 *
 * Allows comparing multiple CVs side-by-side with similarity matrix.
 *
 * @module features/cv/components/CVComparisonModal
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Modal,
  ModalBody,
  ModalFooter,
  Text,
  Badge,
  Button,
  Spinner,
  Card,
} from '@/shared/components/ui';
import { useCompareCVs } from '../hooks';
import type { CVComparisonItem } from '@/shared/types';

// =============================================================================
// Props
// =============================================================================

interface CVComparisonModalProps {
  /** CVs to compare (array of IDs and names for selection) */
  availableCVs: Array<{
    id: string;
    candidate_name: string | null;
    filename: string;
    score: number | null;
  }>;
  /** Pre-selected CV IDs */
  initialSelection?: string[];
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when modal is closed */
  onClose: () => void;
}

// =============================================================================
// Helper Components
// =============================================================================

/** Similarity score cell */
const SimilarityCell = ({ score, isSelf }: { score: number; isSelf: boolean }) => {
  if (isSelf) {
    return (
      <div className="w-12 h-12 flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded">
        <span className="text-gray-400 text-sm">—</span>
      </div>
    );
  }

  const percentage = Math.round(score * 100);
  let bgColor = 'bg-gray-100 dark:bg-gray-800';
  let textColor = 'text-gray-600 dark:text-gray-400';

  if (percentage >= 80) {
    bgColor = 'bg-green-100 dark:bg-green-900/30';
    textColor = 'text-green-700 dark:text-green-400';
  } else if (percentage >= 60) {
    bgColor = 'bg-yellow-100 dark:bg-yellow-900/30';
    textColor = 'text-yellow-700 dark:text-yellow-400';
  }

  return (
    <div
      className={`w-12 h-12 flex items-center justify-center rounded ${bgColor}`}
      title={`${percentage}% similar`}
    >
      <span className={`text-sm font-medium ${textColor}`}>{percentage}%</span>
    </div>
  );
};

/** CV card in comparison */
const ComparisonCard = ({
  cv,
  isWinner,
}: {
  cv: CVComparisonItem;
  isWinner: boolean;
}) => {
  return (
    <Card
      className={`p-4 ${
        isWinner ? 'ring-2 ring-green-500 dark:ring-green-400' : ''
      }`}
    >
      {isWinner && (
        <div className="flex items-center gap-1 mb-2">
          <svg
            className="w-4 h-4 text-green-500"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          <Text size="sm" className="text-green-600 dark:text-green-400 font-medium">
            Best Match
          </Text>
        </div>
      )}

      <Link to={`/history/${cv.cv_id}`}>
        <Text weight="semibold" className="hover:text-blue-600 dark:hover:text-blue-400">
          {cv.candidate_name || 'Unknown Candidate'}
        </Text>
      </Link>
      <Text size="sm" color="muted" className="truncate mb-3">
        {cv.filename}
      </Text>

      <div className="flex items-center gap-2">
        {cv.evaluation_score !== null && (
          <Badge
            variant={
              cv.evaluation_score >= 70
                ? 'success'
                : cv.evaluation_score >= 50
                ? 'warning'
                : 'error'
            }
            size="lg"
          >
            {cv.evaluation_score}%
          </Badge>
        )}
        {cv.status && (
          <Badge
            variant={cv.status === 'pass' ? 'success' : 'error'}
            size="sm"
          >
            {cv.status.toUpperCase()}
          </Badge>
        )}
      </div>
    </Card>
  );
};

// =============================================================================
// Main Component
// =============================================================================

/**
 * Modal for comparing multiple CVs side-by-side.
 *
 * @example
 * ```tsx
 * <CVComparisonModal
 *   availableCVs={cvList}
 *   initialSelection={['uuid1', 'uuid2']}
 *   isOpen={showComparison}
 *   onClose={() => setShowComparison(false)}
 * />
 * ```
 */
export const CVComparisonModal = ({
  availableCVs,
  initialSelection = [],
  isOpen,
  onClose,
}: CVComparisonModalProps) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelection);
  const { mutate: compare, data, isPending, reset } = useCompareCVs();

  // Toggle CV selection
  const toggleSelection = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((i) => i !== id);
      }
      if (prev.length >= 10) {
        return prev; // Max 10 CVs
      }
      return [...prev, id];
    });
  };

  // Start comparison
  const handleCompare = () => {
    if (selectedIds.length >= 2) {
      compare(selectedIds);
    }
  };

  // Reset state when modal closes
  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Compare CVs"
      size="xl"
    >
      <ModalBody>
        {/* Selection Phase */}
        {!data && (
          <>
            <Text color="muted" className="mb-4">
              Select 2-10 CVs to compare side-by-side.
            </Text>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto mb-4">
              {availableCVs.map((cv) => {
                const isSelected = selectedIds.includes(cv.id);
                return (
                  <button
                    key={cv.id}
                    onClick={() => toggleSelection(cv.id)}
                    className={`p-3 rounded-lg border text-left transition-colors ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                          isSelected
                            ? 'border-blue-500 bg-blue-500'
                            : 'border-gray-300 dark:border-gray-600'
                        }`}
                      >
                        {isSelected && (
                          <svg
                            className="w-3 h-3 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={3}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <Text
                          weight="medium"
                          size="sm"
                          className="truncate text-gray-900 dark:text-white"
                        >
                          {cv.candidate_name || 'Unknown'}
                        </Text>
                        <Text size="sm" color="muted" className="truncate">
                          {cv.score !== null ? `${cv.score}%` : 'Not scored'}
                        </Text>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            <Text size="sm" color="muted">
              {selectedIds.length} of {availableCVs.length} selected
              {selectedIds.length < 2 && ' (minimum 2 required)'}
            </Text>
          </>
        )}

        {/* Loading State */}
        {isPending && (
          <div className="flex flex-col items-center justify-center py-12">
            <Spinner size="lg" />
            <Text color="muted" className="mt-4">
              Comparing {selectedIds.length} CVs...
            </Text>
          </div>
        )}

        {/* Results */}
        {data && (
          <div className="space-y-6">
            {/* CV Cards */}
            <div>
              <Text weight="medium" className="mb-3">
                Compared Candidates
              </Text>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.cvs.map((cv) => (
                  <ComparisonCard
                    key={cv.cv_id}
                    cv={cv}
                    isWinner={cv.cv_id === data.best_match_id}
                  />
                ))}
              </div>
            </div>

            {/* Most Similar Pair */}
            {data.most_similar_pair && (
              <Card className="p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-2 mb-2">
                  <svg
                    className="w-5 h-5 text-blue-600 dark:text-blue-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                    />
                  </svg>
                  <Text weight="medium" className="text-blue-900 dark:text-blue-100">
                    Most Similar Pair
                  </Text>
                </div>
                <Text size="sm" className="text-blue-800 dark:text-blue-200">
                  {data.cvs.find((c) => c.cv_id === data.most_similar_pair?.cv1_id)?.candidate_name || 'Unknown'}{' '}
                  and{' '}
                  {data.cvs.find((c) => c.cv_id === data.most_similar_pair?.cv2_id)?.candidate_name || 'Unknown'}{' '}
                  are {Math.round((data.most_similar_pair.similarity || 0) * 100)}% similar
                </Text>
              </Card>
            )}

            {/* Similarity Matrix */}
            <div>
              <Text weight="medium" className="mb-3">
                Similarity Matrix
              </Text>
              <div className="overflow-x-auto">
                <table className="w-auto">
                  <thead>
                    <tr>
                      <th className="p-2"></th>
                      {data.cvs.map((cv, i) => (
                        <th key={cv.cv_id} className="p-2 text-center">
                          <Text size="sm" color="muted" className="truncate max-w-[80px]">
                            {cv.candidate_name?.split(' ')[0] || `CV${i + 1}`}
                          </Text>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.cvs.map((rowCv, rowIndex) => (
                      <tr key={rowCv.cv_id}>
                        <td className="p-2">
                          <Text size="sm" color="muted" className="truncate max-w-[80px]">
                            {rowCv.candidate_name?.split(' ')[0] || `CV${rowIndex + 1}`}
                          </Text>
                        </td>
                        {data.similarity_matrix[rowIndex].map((score, colIndex) => (
                          <td key={colIndex} className="p-1">
                            <SimilarityCell score={score} isSelf={rowIndex === colIndex} />
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </ModalBody>

      <ModalFooter>
        <Button variant="ghost" onClick={handleClose}>
          {data ? 'Close' : 'Cancel'}
        </Button>
        {!data && (
          <Button
            onClick={handleCompare}
            disabled={selectedIds.length < 2 || isPending}
            isLoading={isPending}
          >
            Compare {selectedIds.length} CVs
          </Button>
        )}
        {data && (
          <Button
            variant="outline"
            onClick={() => {
              reset();
            }}
          >
            Compare Different CVs
          </Button>
        )}
      </ModalFooter>
    </Modal>
  );
};
