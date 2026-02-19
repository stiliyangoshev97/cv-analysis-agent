/**
 * @fileoverview Explain Modal Component
 *
 * Modal that shows detailed explanation for a criterion score.
 * Triggered by "Why?" button on criteria items.
 *
 * @module features/chat/components/ExplainModal
 */

import { Button, Text, Heading, Spinner, Badge } from '@/shared/components';
import type { ExplainCriterionResponse } from '@/shared/types';

interface ExplainModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback to close the modal */
  onClose: () => void;
  /** Criterion name being explained */
  criterionName: string;
  /** Whether explanation is loading */
  isLoading: boolean;
  /** Explanation data */
  data?: ExplainCriterionResponse;
  /** Error if request failed */
  error?: Error | null;
}

/**
 * Explain Modal Component
 *
 * Shows detailed AI explanation for why a criterion received its score.
 *
 * @example
 * ```tsx
 * <ExplainModal
 *   isOpen={showExplain}
 *   onClose={() => setShowExplain(false)}
 *   criterionName="Technical Skills"
 *   isLoading={isPending}
 *   data={explanationData}
 * />
 * ```
 */
export const ExplainModal = ({
  isOpen,
  onClose,
  criterionName,
  isLoading,
  data,
  error,
}: ExplainModalProps) => {
  if (!isOpen) return null;

  const scorePercent = data ? Math.round((data.score / data.max_score) * 100) : 0;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        {/* Modal */}
        <div
          className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-lg max-h-[80vh] overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div>
              <Heading level={5} className="text-lg">Why this score?</Heading>
              <Text size="sm" color="muted">{criterionName}</Text>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Spinner size="lg" />
                <Text size="sm" color="muted" className="mt-4">
                  Analyzing criterion...
                </Text>
              </div>
            ) : error ? (
              <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <Text size="sm" className="text-red-600 dark:text-red-400">
                  Failed to load explanation. Please try again.
                </Text>
              </div>
            ) : data ? (
              <div className="space-y-6">
                {/* Score */}
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Text weight="medium">Score:</Text>
                    <Badge
                      variant={scorePercent >= 60 ? 'success' : scorePercent >= 40 ? 'warning' : 'error'}
                      size="lg"
                    >
                      {data.score} / {data.max_score}
                    </Badge>
                  </div>
                  <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        scorePercent >= 60
                          ? 'bg-green-500'
                          : scorePercent >= 40
                          ? 'bg-amber-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${scorePercent}%` }}
                    />
                  </div>
                </div>

                {/* Explanation */}
                <div>
                  <Text weight="medium" className="mb-2">Explanation</Text>
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                    <Text size="sm" className="whitespace-pre-wrap leading-relaxed">
                      {data.explanation}
                    </Text>
                  </div>
                </div>

                {/* Evidence */}
                {data.evidence && data.evidence.length > 0 && (
                  <div>
                    <Text weight="medium" className="mb-2">Evidence from CV</Text>
                    <div className="space-y-2">
                      {data.evidence.map((excerpt, i) => (
                        <div
                          key={i}
                          className="bg-blue-50 dark:bg-blue-950/30 border-l-4 border-blue-400 dark:border-blue-500 rounded-r-lg p-3"
                        >
                          <Text size="sm" className="text-blue-800 dark:text-blue-200 italic">
                            "{excerpt}"
                          </Text>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <Button variant="outline" onClick={onClose} className="w-full">
              Close
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};
