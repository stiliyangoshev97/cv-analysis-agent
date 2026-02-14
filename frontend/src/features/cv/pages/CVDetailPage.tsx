/**
 * @fileoverview CV Detail Page.
 *
 * Displays detailed information about a CV including evaluation results.
 *
 * @module features/cv/pages/CVDetailPage
 */

import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Heading,
  Text,
  Card,
  Badge,
  Button,
  Spinner,
  Modal,
  ModalBody,
  ModalFooter,
} from '@/shared/components/ui';
import { useCV, useDeleteCV } from '../hooks';
import { ChatPanel } from '@/features/chat';

// =============================================================================
// Helper Components
// =============================================================================

/** Score badge with color based on value */
const ScoreBadge = ({ score }: { score: number }) => {
  let variant: 'success' | 'warning' | 'error' = 'error';
  if (score >= 70) variant = 'success';
  else if (score >= 50) variant = 'warning';

  return (
    <Badge variant={variant} size="lg">
      {score}%
    </Badge>
  );
};

/** Status badge */
const StatusBadge = ({ status }: { status: string }) => {
  const variant = status === 'pass' ? 'success' : 'error';
  return (
    <Badge variant={variant} size="sm">
      {status.toUpperCase()}
    </Badge>
  );
};

/** Format date string */
const formatDate = (isoString: string): string => {
  const date = new Date(isoString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// =============================================================================
// Criteria Results Component
// =============================================================================

interface CriteriaResultsProps {
  criteriaResults: Record<string, {
    score: number;
    max_score: number;
    reasoning: string;
    evidence: string[];
  }>;
}

const CriteriaResults = ({ criteriaResults }: CriteriaResultsProps) => {
  return (
    <div className="space-y-4">
      {Object.entries(criteriaResults).map(([name, result]) => {
        const percentage = Math.round((result.score / result.max_score) * 100);
        let colorClass = 'bg-red-500';
        if (percentage >= 70) colorClass = 'bg-green-500';
        else if (percentage >= 50) colorClass = 'bg-yellow-500';

        return (
          <Card key={name} className="p-4">
            <div className="flex items-center justify-between mb-2">
              <Text weight="medium" className="text-gray-900 dark:text-white">
                {name}
              </Text>
              <Text size="sm" className="text-gray-600 dark:text-gray-400">
                {result.score} / {result.max_score} pts
              </Text>
            </div>
            
            {/* Progress bar */}
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
              <div
                className={`${colorClass} h-2 rounded-full transition-all`}
                style={{ width: `${percentage}%` }}
              />
            </div>
            
            <Text size="sm" color="muted" className="mb-2">
              {result.reasoning}
            </Text>
            
            {result.evidence && result.evidence.length > 0 && (
              <div className="mt-2">
                <Text size="sm" weight="medium" className="text-gray-700 dark:text-gray-300 mb-1">
                  Evidence:
                </Text>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400">
                  {result.evidence.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
};

// =============================================================================
// Main Component
// =============================================================================

/**
 * CV Detail Page
 *
 * Shows full CV details including evaluation results.
 */
export const CVDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: cv, isLoading, error } = useCV(id!);
  const { mutate: deleteCV, isPending: isDeleting } = useDeleteCV();

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showChat, setShowChat] = useState(false);

  if (isLoading) {
    return (
      <Container>
        <div className="flex justify-center items-center py-20">
          <Spinner size="lg" />
        </div>
      </Container>
    );
  }

  if (error || !cv) {
    return (
      <Container>
        <Card className="p-8 text-center">
          <svg
            className="w-12 h-12 mx-auto text-red-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <Text color="muted">CV not found</Text>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => navigate('/history')}
          >
            Back to History
          </Button>
        </Card>
      </Container>
    );
  }

  const handleDelete = () => {
    deleteCV(cv.id, {
      onSuccess: () => {
        setShowDeleteModal(false);
        navigate('/history');
      },
    });
  };

  return (
    <Container>
      {/* Breadcrumb */}
      <nav className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <li>
            <Link
              to="/history"
              className="hover:text-blue-600 dark:hover:text-blue-400"
            >
              History
            </Link>
          </li>
          <li>/</li>
          <li className="text-gray-900 dark:text-white">
            {cv.candidate_name || cv.filename}
          </li>
        </ol>
      </nav>

      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <Heading level={1}>
              {cv.candidate_name || 'Unknown Candidate'}
            </Heading>
            {cv.evaluation && (
              <ScoreBadge score={cv.evaluation.score} />
            )}
          </div>
          <Text color="muted" className="mt-1">
            {cv.filename}
          </Text>
          <Text size="sm" color="muted" className="mt-1">
            Uploaded {formatDate(cv.uploaded_at)}
          </Text>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setShowChat(true)}
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            Ask AI
          </Button>
          <Button
            variant="danger"
            onClick={() => setShowDeleteModal(true)}
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
            Delete
          </Button>
        </div>
      </div>

      {/* Evaluation Results */}
      {cv.evaluation ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Summary */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="p-6">
              <Heading level={3} className="mb-4">
                Summary
              </Heading>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Text color="muted">Status</Text>
                  <StatusBadge status={cv.evaluation.status} />
                </div>
                <div className="flex items-center justify-between">
                  <Text color="muted">Score</Text>
                  <Text weight="semibold" className="text-gray-900 dark:text-white">
                    {cv.evaluation.score}%
                  </Text>
                </div>
                <div className="flex items-center justify-between">
                  <Text color="muted">Evaluated</Text>
                  <Text size="sm" className="text-gray-700 dark:text-gray-300">
                    {formatDate(cv.evaluation.evaluated_at)}
                  </Text>
                </div>
              </div>
            </Card>

            {cv.evaluation.reasoning && (
              <Card className="p-6">
                <Heading level={3} className="mb-4">
                  AI Analysis
                </Heading>
                <Text color="muted" className="whitespace-pre-wrap">
                  {cv.evaluation.reasoning}
                </Text>
              </Card>
            )}
          </div>

          {/* Right: Criteria Results */}
          <div className="lg:col-span-2">
            <Heading level={3} className="mb-4">
              Criteria Scores
            </Heading>
            {cv.evaluation.criteria_results ? (
              <CriteriaResults criteriaResults={cv.evaluation.criteria_results} />
            ) : (
              <Card className="p-8 text-center">
                <Text color="muted">No detailed criteria results available</Text>
              </Card>
            )}
          </div>
        </div>
      ) : (
        <Card className="p-8 text-center">
          <svg
            className="w-12 h-12 mx-auto text-yellow-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <Heading level={3}>No Evaluation Available</Heading>
          <Text color="muted" className="mt-2">
            This CV has not been evaluated yet or the evaluation failed.
          </Text>
        </Card>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete CV"
        size="sm"
      >
        <ModalBody>
          <Text>
            Are you sure you want to delete{' '}
            <span className="font-semibold">
              "{cv.candidate_name || cv.filename}"
            </span>
            ?
          </Text>
          <Text color="muted" size="sm" className="mt-2">
            This will permanently remove the CV, all evaluations, embeddings, and chat
            history associated with it. This action cannot be undone.
          </Text>
        </ModalBody>

        <ModalFooter>
          <Button
            type="button"
            variant="ghost"
            onClick={() => setShowDeleteModal(false)}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleDelete}
            isLoading={isDeleting}
            disabled={isDeleting}
          >
            Delete CV
          </Button>
        </ModalFooter>
      </Modal>

      {/* Chat Panel */}
      <ChatPanel
        cvId={cv.id}
        candidateName={cv.candidate_name ?? undefined}
        isOpen={showChat}
        onClose={() => setShowChat(false)}
      />
    </Container>
  );
};
