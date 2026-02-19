/**
 * @fileoverview Scorecard Component
 *
 * Displays the CV evaluation results in a card format.
 * Shows pass/fail status, match score, AI reasoning, and criteria breakdown.
 *
 * @module features/cv/components/Scorecard
 *
 * FEATURES:
 * - Pass/Fail status with color-coded header
 * - Visual score ring showing match percentage
 * - AI reasoning explanation
 * - Individual criteria breakdown with pass/fail indicators
 * - "Ask AI" button for chat panel
 * - Dismiss action button
 *
 * @example
 * ```tsx
 * <Scorecard
 *   result={{
 *     id: '123',
 *     filename: 'resume.pdf',
 *     evaluation: evaluationData,
 *     uploadedAt: new Date(),
 *   }}
 *   onDismiss={() => setResult(null)}
 * />
 * ```
 */

import { useState } from 'react';
import { Badge, Button, Card, CardContent, CardFooter, Text, Heading } from '@/shared/components/ui';
import type { CVResult } from '@/shared/types';
import { CriteriaItem } from './CriteriaItem';
import { ScoreRing } from './ScoreRing';
import { ChatPanel } from '@/features/chat';

/**
 * Scorecard component props.
 */
interface ScorecardProps {
  /** CV evaluation result to display */
  result: CVResult;
  /** Callback when user dismisses the scorecard */
  onDismiss: () => void;
}

/**
 * Scorecard Component
 *
 * Displays a comprehensive CV evaluation result card with
 * status, score, reasoning, and criteria breakdown.
 *
 * @param props - Component props
 * @returns Scorecard element
 */
export const Scorecard = ({ result, onDismiss }: ScorecardProps) => {
  const [showChat, setShowChat] = useState(false);
  const { evaluation, filename } = result;
  const isPassed = evaluation.status === 'pass';

  return (
    <Card padding="none" className="overflow-hidden">
      {/* Header */}
      <div className={`px-6 py-4 ${isPassed ? 'bg-green-50 dark:bg-green-950/30 border-b border-green-100 dark:border-green-800' : 'bg-red-50 dark:bg-red-950/30 border-b border-red-100 dark:border-red-800'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isPassed ? 'bg-green-100 dark:bg-green-900/50' : 'bg-red-100 dark:bg-red-900/50'}`}>
              {isPassed ? (
                <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>
            <div>
              <Heading level={5} className="font-semibold text-gray-900 dark:text-white">
                {evaluation.candidate_name || 'Unknown Candidate'}
              </Heading>
              <Text variant="muted" size="sm">{filename}</Text>
            </div>
          </div>
          <Badge variant={isPassed ? 'success' : 'error'} size="lg">
            {isPassed ? 'PASSED' : 'FAILED'}
          </Badge>
        </div>
      </div>

      {/* Body */}
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Score Ring */}
          <div className="flex justify-center md:justify-start">
            <ScoreRing score={evaluation.match_score} />
          </div>

          {/* Reasoning */}
          <div className="flex-1">
            <Text weight="semibold" size="sm" className="mb-2 text-gray-900 dark:text-white">AI Assessment</Text>
            <Text variant="muted" size="sm" className="leading-relaxed">
              {evaluation.reasoning}
            </Text>
          </div>
        </div>

        {/* Criteria */}
        <div className="mt-6">
          <Text weight="semibold" size="sm" className="mb-3 text-gray-900 dark:text-white">Evaluation Criteria</Text>
          <div className="space-y-2">
            {evaluation.criteria.map((criterion, index) => (
              <CriteriaItem key={index} criteria={criterion} cvId={result.id} />
            ))}
          </div>
        </div>
      </CardContent>

      {/* Footer */}
      <CardFooter className="px-6 py-4 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-700 flex justify-between mt-0">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowChat(true)}
          className="gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Ask AI
        </Button>
        <Button variant="ghost" size="sm" onClick={onDismiss}>
          Dismiss
        </Button>
      </CardFooter>

      {/* Chat Panel */}
      <ChatPanel
        cvId={result.id}
        candidateName={evaluation.candidate_name ?? undefined}
        isOpen={showChat}
        onClose={() => setShowChat(false)}
      />
    </Card>
  );
};
