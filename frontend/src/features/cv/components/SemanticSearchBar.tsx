/**
 * @fileoverview Semantic Search Bar component.
 *
 * Natural language search for CVs using vector embeddings.
 *
 * @module features/cv/components/SemanticSearchBar
 */

import { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  Card,
  Text,
  Badge,
  Button,
  Input,
} from '@/shared/components/ui';
import { useSearchCVsMutation } from '../hooks';
import type { SimilarCV } from '@/shared/types';

// =============================================================================
// Props
// =============================================================================

interface SemanticSearchBarProps {
  /** Callback when search results are available */
  onResults?: (results: SimilarCV[]) => void;
  /** Callback when search is cleared */
  onClear?: () => void;
  /** Placeholder text */
  placeholder?: string;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Semantic search bar for finding CVs by natural language query.
 *
 * @example
 * ```tsx
 * <SemanticSearchBar
 *   onResults={(results) => setSearchResults(results)}
 *   onClear={() => setSearchResults(null)}
 * />
 * ```
 */
export const SemanticSearchBar = ({
  onResults,
  onClear,
  placeholder = 'Search by skills, experience... (e.g., "Python developer with fintech experience")',
}: SemanticSearchBarProps) => {
  const [query, setQuery] = useState('');
  const { mutate: search, data, isPending, reset } = useSearchCVsMutation();

  const handleSearch = useCallback(() => {
    if (query.length >= 3) {
      search(
        { query, limit: 20 },
        {
          onSuccess: (data) => {
            onResults?.(data.results);
          },
        }
      );
    }
  }, [query, search, onResults]);

  const handleClear = useCallback(() => {
    setQuery('');
    reset();
    onClear?.();
  }, [reset, onClear]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleSearch();
      } else if (e.key === 'Escape') {
        handleClear();
      }
    },
    [handleSearch, handleClear]
  );

  return (
    <div className="w-full">
      <div className="relative flex gap-2">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg
              className="h-5 w-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="pl-10 pr-4"
          />
        </div>
        <Button
          onClick={handleSearch}
          disabled={query.length < 3 || isPending}
          isLoading={isPending}
        >
          Search
        </Button>
        {(query || data) && (
          <Button variant="ghost" onClick={handleClear}>
            Clear
          </Button>
        )}
      </div>

      {/* Search hint */}
      {query.length > 0 && query.length < 3 && (
        <Text size="sm" color="muted" className="mt-1">
          Enter at least 3 characters to search
        </Text>
      )}
    </div>
  );
};

// =============================================================================
// Search Results Component
// =============================================================================

interface SearchResultsProps {
  /** Search results to display */
  results: SimilarCV[];
  /** Search query for display */
  query: string;
  /** Whether to show inline or as overlay */
  inline?: boolean;
}

/**
 * Displays semantic search results.
 *
 * @example
 * ```tsx
 * <SearchResults
 *   results={searchResults}
 *   query="Python developer"
 * />
 * ```
 */
export const SearchResults = ({
  results,
  query,
  inline = true,
}: SearchResultsProps) => {
  if (results.length === 0) {
    return (
      <Card className="p-6 text-center">
        <svg
          className="w-10 h-10 mx-auto text-gray-400 mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <Text color="muted">No CVs match "{query}"</Text>
        <Text size="sm" color="muted" className="mt-1">
          Try a different search query
        </Text>
      </Card>
    );
  }

  return (
    <div className={inline ? 'space-y-3' : ''}>
      <div className="flex items-center justify-between mb-3">
        <Text size="sm" color="muted">
          Found {results.length} matching CV{results.length !== 1 ? 's' : ''} for "{query}"
        </Text>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {results.map((cv) => (
          <Link
            key={cv.cv_id}
            to={`/history/${cv.cv_id}`}
            className="block"
          >
            <Card className="p-4 hover:shadow-md transition-shadow h-full">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <Text
                    weight="medium"
                    className="truncate text-gray-900 dark:text-white"
                  >
                    {cv.candidate_name || 'Unknown Candidate'}
                  </Text>
                  <Text size="sm" color="muted" className="truncate">
                    {cv.filename}
                  </Text>
                </div>
                <Badge
                  variant={cv.similarity_score >= 0.7 ? 'success' : 'neutral'}
                  size="sm"
                >
                  {Math.round(cv.similarity_score * 100)}% relevant
                </Badge>
              </div>

              {cv.evaluation_score !== null && (
                <div className="flex items-center gap-2 mt-3">
                  <Badge
                    variant={
                      cv.evaluation_score >= 70
                        ? 'success'
                        : cv.evaluation_score >= 50
                        ? 'warning'
                        : 'error'
                    }
                    size="sm"
                  >
                    {cv.evaluation_score}%
                  </Badge>
                  {cv.status && (
                    <Badge
                      variant={cv.status === 'pass' ? 'success' : 'error'}
                      size="sm"
                    >
                      {cv.status.toUpperCase()}
                    </Badge>
                  )}
                </div>
              )}
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
};
