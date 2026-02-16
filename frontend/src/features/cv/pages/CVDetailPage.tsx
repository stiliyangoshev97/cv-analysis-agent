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
  Button,
  Spinner,
  Modal,
  ModalBody,
  ModalFooter,
} from '@/shared/components/ui';
import { useCV, useDeleteCV } from '../hooks';
import { ChatPanel } from '@/features/chat';
import { SimilarCVsModal, RankingBadge, ReEvaluateModal } from '../components';

// =============================================================================
// Helper Components
// =============================================================================

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
  const [showSimilar, setShowSimilar] = useState(false);
  const [showReEvaluate, setShowReEvaluate] = useState(false);

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

      {/* Hero Header Card */}
      <Card className="mb-6 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-600 dark:from-blue-800 dark:via-blue-700 dark:to-indigo-800 p-6">
          <div className="flex items-start justify-between gap-4">
            {/* Left: Candidate Info */}
            <div className="flex items-start gap-4">
              {/* Avatar with initials */}
              <div className="flex-shrink-0 w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {(cv.candidate_name || 'UC').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
                </span>
              </div>
              
              <div>
                <h1 className="text-2xl font-bold text-white mb-1">
                  {cv.candidate_name || 'Unknown Candidate'}
                </h1>
                <div className="flex items-center gap-2 text-blue-100">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm">{cv.filename}</span>
                </div>
                <div className="flex items-center gap-2 text-blue-100 mt-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm">Uploaded {formatDate(cv.uploaded_at)}</span>
                </div>
              </div>
            </div>

            {/* Right: Score & Status */}
            {cv.evaluation && (
              <div className="flex flex-col items-end gap-2">
                <div className="flex items-center gap-3">
                  <div className={`px-4 py-2 rounded-xl font-bold text-lg ${
                    cv.evaluation.score >= 70 
                      ? 'bg-green-500 text-white' 
                      : cv.evaluation.score >= 50 
                        ? 'bg-yellow-500 text-white' 
                        : 'bg-red-500 text-white'
                  }`}>
                    {cv.evaluation.score}%
                  </div>
                  <RankingBadge cvId={cv.id} showDetails />
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  cv.evaluation.status === 'pass'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'
                }`}>
                  {cv.evaluation.status.toUpperCase()}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action buttons bar */}
        <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSimilar(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 hover:border-blue-300 dark:hover:border-blue-500 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Find Similar
            </button>
            <button
              onClick={() => setShowChat(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 hover:border-purple-300 dark:hover:border-purple-500 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Ask AI
            </button>
            <button
              onClick={() => setShowReEvaluate(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 hover:border-amber-300 dark:hover:border-amber-500 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Re-evaluate
            </button>
          </div>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-red-600 dark:text-red-400 bg-white dark:bg-gray-700 border border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        </div>
      </Card>

      {/* Evaluation Results */}
      {cv.evaluation ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: AI Analysis & Evaluation Info */}
          <div className="lg:col-span-1 space-y-4">
            {/* Evaluation Meta Card */}
            <Card className="p-5">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <Heading level={4}>Evaluated on</Heading>
              </div>
              <Text size="sm" color="muted">
                {formatDate(cv.evaluation.evaluated_at)}
              </Text>
            </Card>

            {cv.evaluation.reasoning && (
              <Card className="p-5">
                <div className="flex items-center gap-2 mb-3">
                  <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <Heading level={4}>AI Analysis</Heading>
                </div>
                <Text color="muted" size="sm" className="whitespace-pre-wrap leading-relaxed">
                  {cv.evaluation.reasoning}
                </Text>
              </Card>
            )}
          </div>

          {/* Right: Criteria Results */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <Heading level={3}>Criteria Scores</Heading>
            </div>
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

      {/* Similar CVs Modal */}
      <SimilarCVsModal
        cvId={cv.id}
        candidateName={cv.candidate_name ?? undefined}
        isOpen={showSimilar}
        onClose={() => setShowSimilar(false)}
      />

      {/* Re-evaluate Modal */}
      <ReEvaluateModal
        cvId={cv.id}
        candidateName={cv.candidate_name ?? undefined}
        isOpen={showReEvaluate}
        onClose={() => setShowReEvaluate(false)}
      />
    </Container>
  );
};
