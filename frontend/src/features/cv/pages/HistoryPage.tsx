/**
 * @fileoverview CV Evaluation History Page.
 *
 * Displays a paginated list of all CVs the user has evaluated,
 * with scores, statuses, and quick actions.
 *
 * @module features/cv/pages/HistoryPage
 */

import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Heading,
  Text,
  Card,
  Badge,
  Button,
  Spinner,
  Input,
  Modal,
  ModalBody,
  ModalFooter,
} from '@/shared/components/ui';
import { useCVList, useDeleteCV } from '../hooks';
import {
  SemanticSearchBar,
  SearchResults,
  CVComparisonModal,
  RankingInline,
} from '../components';
import type { CVSummary, SimilarCV } from '@/shared/schemas';

// =============================================================================
// Helper Components
// =============================================================================

/** Score badge with color based on value */
const ScoreBadge = ({ score }: { score: number | null }) => {
  if (score === null) {
    return (
      <Badge variant="neutral" size="sm">
        Pending
      </Badge>
    );
  }

  let variant: 'success' | 'warning' | 'error' = 'error';
  if (score >= 70) variant = 'success';
  else if (score >= 50) variant = 'warning';

  return (
    <Badge variant={variant} size="sm">
      {score}%
    </Badge>
  );
};

/** Status badge */
const StatusBadge = ({ status }: { status: string | null }) => {
  if (!status) {
    return (
      <Badge variant="neutral" size="sm">
        N/A
      </Badge>
    );
  }

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
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

/** Format relative time */
const formatRelativeTime = (isoString: string): string => {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return `${Math.floor(diffDays / 30)} months ago`;
};

// =============================================================================
// CV History Item
// =============================================================================

interface CVHistoryItemProps {
  cv: CVSummary;
  onDelete: (cv: CVSummary) => void;
}

const CVHistoryItem = ({ cv, onDelete }: CVHistoryItemProps) => {
  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="flex-shrink-0">
          <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <Text weight="medium" className="truncate text-gray-900 dark:text-white">
                {cv.candidate_name || 'Unknown Candidate'}
              </Text>
              <Text size="sm" color="muted" className="truncate">
                {cv.filename}
              </Text>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <ScoreBadge score={cv.score} />
              <StatusBadge status={cv.evaluation_status} />
              {cv.evaluation_status && <RankingInline cvId={cv.id} />}
            </div>
          </div>

          {/* Meta info */}
          <div className="flex items-center gap-4 mt-2">
            <Text size="sm" color="muted" className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {formatRelativeTime(cv.uploaded_at)}
            </Text>
            <Text size="sm" color="muted" className="hidden sm:block">
              {formatDate(cv.uploaded_at)}
            </Text>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(cv)}
            className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
            title="Delete CV"
          >
            <svg
              className="w-4 h-4"
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
          </Button>
          <Link to={`/history/${cv.id}`}>
            <Button variant="ghost" size="sm" title="View details">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Button>
          </Link>
        </div>
      </div>
    </Card>
  );
};

// =============================================================================
// History Stats
// =============================================================================

interface HistoryStatsProps {
  cvs: CVSummary[];
}

const HistoryStats = ({ cvs }: HistoryStatsProps) => {
  const stats = useMemo(() => {
    const evaluated = cvs.filter((cv) => cv.score !== null);
    const passed = cvs.filter((cv) => cv.evaluation_status === 'pass');
    const avgScore =
      evaluated.length > 0
        ? Math.round(evaluated.reduce((sum, cv) => sum + (cv.score || 0), 0) / evaluated.length)
        : 0;

    return {
      total: cvs.length,
      evaluated: evaluated.length,
      passed: passed.length,
      failed: evaluated.length - passed.length,
      avgScore,
      passRate: evaluated.length > 0 ? Math.round((passed.length / evaluated.length) * 100) : 0,
    };
  }, [cvs]);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <Card className="p-4">
        <Text size="sm" color="muted">
          Total CVs
        </Text>
        <Text size="lg" weight="semibold" className="text-gray-900 dark:text-white">
          {stats.total}
        </Text>
      </Card>
      <Card className="p-4">
        <Text size="sm" color="muted">
          Avg. Score
        </Text>
        <Text size="lg" weight="semibold" className="text-gray-900 dark:text-white">
          {stats.avgScore}%
        </Text>
      </Card>
      <Card className="p-4">
        <Text size="sm" color="muted">
          Passed
        </Text>
        <Text size="lg" weight="semibold" className="text-green-600 dark:text-green-400">
          {stats.passed}
        </Text>
      </Card>
      <Card className="p-4">
        <Text size="sm" color="muted">
          Pass Rate
        </Text>
        <Text size="lg" weight="semibold" className="text-blue-600 dark:text-blue-400">
          {stats.passRate}%
        </Text>
      </Card>
    </div>
  );
};

// =============================================================================
// Main Component
// =============================================================================

/**
 * CV Evaluation History Page
 *
 * Shows all CVs the user has evaluated with filtering and sorting.
 */
export const HistoryPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'pass' | 'fail'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'score'>('date');
  const [cvToDelete, setCvToDelete] = useState<CVSummary | null>(null);
  const [showComparison, setShowComparison] = useState(false);
  const [searchResults, setSearchResults] = useState<SimilarCV[] | null>(null);
  const [searchQueryText, setSearchQueryText] = useState('');

  const { data, isLoading, error } = useCVList(100, 0);
  const { mutate: deleteCV, isPending: isDeleting } = useDeleteCV();

  // Handle delete confirmation
  const handleDeleteClick = (cv: CVSummary) => {
    setCvToDelete(cv);
  };

  const handleDeleteConfirm = () => {
    if (!cvToDelete) return;
    deleteCV(cvToDelete.id, {
      onSuccess: () => {
        setCvToDelete(null);
      },
    });
  };

  const handleDeleteCancel = () => {
    setCvToDelete(null);
  };

  // Filter and sort CVs
  const filteredCVs = useMemo(() => {
    if (!data?.cvs) return [];

    let filtered = [...data.cvs];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (cv) =>
          cv.candidate_name?.toLowerCase().includes(query) ||
          cv.filename.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter((cv) => cv.evaluation_status === filterStatus);
    }

    // Sort
    if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime());
    } else if (sortBy === 'score') {
      filtered.sort((a, b) => (b.score || 0) - (a.score || 0));
    }

    return filtered;
  }, [data?.cvs, searchQuery, filterStatus, sortBy]);

  if (isLoading) {
    return (
      <Container>
        <div className="flex justify-center items-center py-20">
          <Spinner size="lg" />
        </div>
      </Container>
    );
  }

  if (error) {
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
          <Text color="muted">Failed to load evaluation history</Text>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        </Card>
      </Container>
    );
  }

  const cvs = data?.cvs || [];

  return (
    <Container>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Heading level={1}>Evaluation History</Heading>
          <Text color="muted" className="mt-1">
            View and manage your CV evaluations
          </Text>
        </div>
        <div className="flex items-center gap-2">
          {cvs.length >= 2 && (
            <Button variant="outline" onClick={() => setShowComparison(true)}>
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              Compare CVs
            </Button>
          )}
          <Link to="/">
            <Button>
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
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Upload CV
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats */}
      {cvs.length > 0 && <HistoryStats cvs={cvs} />}

      {/* Semantic Search */}
      {cvs.length > 0 && (
        <Card className="p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <svg
              className="w-5 h-5 text-blue-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <Text weight="medium" className="text-gray-900 dark:text-white">
              AI-Powered Search
            </Text>
          </div>
          <SemanticSearchBar
            onResults={(results) => {
              setSearchResults(results);
              setSearchQueryText(results.length > 0 ? 'search results' : '');
            }}
            onClear={() => {
              setSearchResults(null);
              setSearchQueryText('');
            }}
          />
        </Card>
      )}

      {/* Search Results */}
      {searchResults && (
        <div className="mb-6">
          <SearchResults results={searchResults} query={searchQueryText} />
        </div>
      )}

      {/* Filters (only show when not in search mode) */}
      {cvs.length > 0 && !searchResults && (
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          {/* Search */}
          <div className="flex-1">
            <Input
              placeholder="Filter by name or filename..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as 'all' | 'pass' | 'fail')}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="pass">Passed</option>
              <option value="fail">Failed</option>
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'score')}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="date">Sort by Date</option>
              <option value="score">Sort by Score</option>
            </select>
          </div>
        </div>
      )}

      {/* Empty State */}
      {cvs.length === 0 && (
        <Card className="p-12 text-center">
          <svg
            className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <Heading level={3}>No evaluations yet</Heading>
          <Text color="muted" className="mt-2 mb-6">
            Upload your first CV to get started with AI-powered screening.
          </Text>
          <Link to="/">
            <Button>Upload Your First CV</Button>
          </Link>
        </Card>
      )}

      {/* No Results */}
      {cvs.length > 0 && filteredCVs.length === 0 && (
        <Card className="p-8 text-center">
          <svg
            className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <Text color="muted">No CVs match your filters</Text>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => {
              setSearchQuery('');
              setFilterStatus('all');
            }}
          >
            Clear Filters
          </Button>
        </Card>
      )}

      {/* CV List */}
      {filteredCVs.length > 0 && (
        <div className="space-y-3">
          {filteredCVs.map((cv) => (
            <CVHistoryItem key={cv.id} cv={cv} onDelete={handleDeleteClick} />
          ))}
        </div>
      )}

      {/* Results Count */}
      {filteredCVs.length > 0 && (
        <div className="mt-4 text-center">
          <Text size="sm" color="muted">
            Showing {filteredCVs.length} of {cvs.length} evaluations
          </Text>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!cvToDelete}
        onClose={handleDeleteCancel}
        title="Delete CV"
        size="sm"
      >
        <ModalBody>
          <Text>
            Are you sure you want to delete{' '}
            <span className="font-semibold">
              "{cvToDelete?.candidate_name || cvToDelete?.filename}"
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
            onClick={handleDeleteCancel}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleDeleteConfirm}
            isLoading={isDeleting}
            disabled={isDeleting}
          >
            Delete CV
          </Button>
        </ModalFooter>
      </Modal>

      {/* CV Comparison Modal */}
      <CVComparisonModal
        availableCVs={cvs.map((cv) => ({
          id: cv.id,
          candidate_name: cv.candidate_name,
          filename: cv.filename,
          score: cv.score,
        }))}
        isOpen={showComparison}
        onClose={() => setShowComparison(false)}
      />
    </Container>
  );
};
