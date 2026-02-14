/**
 * @fileoverview CriteriaItem Component
 *
 * Displays a single evaluation criterion with pass/fail status.
 * Used within the Scorecard to show individual hiring criteria results.
 * Includes "Why?" button to get AI explanation for the score.
 *
 * @module features/cv/components/CriteriaItem
 *
 * FEATURES:
 * - Pass/fail icon indicator
 * - Criterion name and status badge
 * - Detailed explanation text
 * - Color-coded visual feedback
 * - "Why?" button for AI explanations
 *
 * @example
 * ```tsx
 * <CriteriaItem
 *   criteria={{
 *     name: 'Education',
 *     passed: true,
 *     details: 'Candidate has a Bachelor degree in Computer Science',
 *   }}
 *   cvId="cv-uuid"
 * />
 * ```
 */

import { useState } from 'react';
import { Badge, Button, Text } from '@/shared/components/ui';
import type { EvaluationCriteria } from '@/shared/types';
import { useExplainCriterion, ExplainModal } from '@/features/chat';

/**
 * CriteriaItem component props.
 */
interface CriteriaItemProps {
  /** Evaluation criteria data */
  criteria: EvaluationCriteria;
  /** CV ID for explain requests */
  cvId?: string;
}

/**
 * CriteriaItem Component
 *
 * Displays a single hiring criterion evaluation result with
 * option to get AI explanation.
 *
 * @param props - Component props
 * @returns Criteria item element
 */
export const CriteriaItem = ({ criteria, cvId }: CriteriaItemProps) => {
  const [showExplain, setShowExplain] = useState(false);
  const { mutate: explain, isPending, data, error, reset } = useExplainCriterion();

  const handleWhyClick = () => {
    if (!cvId) return;
    setShowExplain(true);
    explain({ cvId, criterion: criteria.name });
  };

  const handleCloseExplain = () => {
    setShowExplain(false);
    reset();
  };

  return (
    <>
      <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
        <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
          criteria.passed ? 'bg-green-100' : 'bg-red-100'
        }`}>
          {criteria.passed ? (
            <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-3 h-3 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Text as="span" weight="semibold" size="sm">{criteria.name}</Text>
            <Badge variant={criteria.passed ? 'success' : 'error'} size="sm">
              {criteria.passed ? 'Passed' : 'Failed'}
            </Badge>
            {cvId && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleWhyClick}
                className="ml-auto text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-2 py-1 h-auto text-xs"
              >
                Why?
              </Button>
            )}
          </div>
          <Text variant="muted" size="sm">{criteria.details}</Text>
        </div>
      </div>

      {/* Explain Modal */}
      <ExplainModal
        isOpen={showExplain}
        onClose={handleCloseExplain}
        criterionName={criteria.name}
        isLoading={isPending}
        data={data}
        error={error}
      />
    </>
  );
};
