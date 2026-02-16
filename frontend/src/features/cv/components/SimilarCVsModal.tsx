/**
 * @fileoverview Similar CVs Modal component.
 *
 * Displays CVs similar to a given CV with similarity scores.
 *
 * @module features/cv/components/SimilarCVsModal
 */

import { Link } from 'react-router-dom';
import {
  Modal,
  ModalBody,
  Text,
  Badge,
  Spinner,
  Button,
} from '@/shared/components/ui';
import { useSimilarCVs } from '../hooks';

// =============================================================================
// Props
// =============================================================================

interface SimilarCVsModalProps {
  /** The source CV ID */
  cvId: string;
  /** Candidate name for display */
  candidateName?: string;
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when modal is closed */
  onClose: () => void;
}

// =============================================================================
// Helper Components
// =============================================================================

/** Similarity score badge */
const SimilarityBadge = ({ score }: { score: number }) => {
  const percentage = Math.round(score * 100);
  let variant: 'success' | 'warning' | 'neutral' = 'neutral';
  if (percentage >= 80) variant = 'success';
  else if (percentage >= 60) variant = 'warning';

  return (
    <Badge variant={variant} size="sm">
      {percentage}% match
    </Badge>
  );
};

/** Score badge */
const ScoreBadge = ({ score }: { score: number | null }) => {
  if (score === null) return null;

  let variant: 'success' | 'warning' | 'error' = 'error';
  if (score >= 70) variant = 'success';
  else if (score >= 50) variant = 'warning';

  return (
    <Badge variant={variant} size="sm">
      {score}%
    </Badge>
  );
};

// =============================================================================
// Main Component
// =============================================================================

/**
 * Modal showing CVs similar to a given CV.
 *
 * @example
 * ```tsx
 * <SimilarCVsModal
 *   cvId="uuid"
 *   candidateName="John Doe"
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 * />
 * ```
 */
export const SimilarCVsModal = ({
  cvId,
  candidateName,
  isOpen,
  onClose,
}: SimilarCVsModalProps) => {
  // Use 0.5 (50%) minimum similarity to filter out dissimilar CVs
  const { data, isLoading, error } = useSimilarCVs(cvId, 10, 0.5, isOpen);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Similar to ${candidateName || 'this CV'}`}
      size="lg"
    >
      <ModalBody>
        {isLoading && (
          <div className="flex justify-center py-8">
            <Spinner size="lg" />
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <Text color="muted">Failed to find similar CVs</Text>
            <Text size="sm" color="muted" className="mt-1">
              {error.message}
            </Text>
          </div>
        )}

        {data && data.similar_cvs.length === 0 && (
          <div className="text-center py-8">
            <svg
              className="w-12 h-12 mx-auto text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            <Text color="muted">No similar CVs found</Text>
            <Text size="sm" color="muted" className="mt-1">
              Upload more CVs to find similar candidates
            </Text>
          </div>
        )}

        {data && data.similar_cvs.length > 0 && (
          <div className="space-y-3">
            <Text size="sm" color="muted" className="mb-4">
              Found {data.total} similar candidate{data.total !== 1 ? 's' : ''}
            </Text>

            {data.similar_cvs.map((cv) => (
              <Link
                key={cv.cv_id}
                to={`/history/${cv.cv_id}`}
                onClick={onClose}
                className="block p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Text
                        weight="medium"
                        className="truncate text-gray-900 dark:text-white"
                      >
                        {cv.candidate_name || 'Unknown Candidate'}
                      </Text>
                      <SimilarityBadge score={cv.similarity_score} />
                    </div>
                    <Text size="sm" color="muted" className="truncate">
                      {cv.filename}
                    </Text>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <ScoreBadge score={cv.evaluation_score} />
                    {cv.status && (
                      <Badge
                        variant={cv.status === 'pass' ? 'success' : 'error'}
                        size="sm"
                      >
                        {cv.status.toUpperCase()}
                      </Badge>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        <div className="flex justify-end mt-6">
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>
      </ModalBody>
    </Modal>
  );
};
