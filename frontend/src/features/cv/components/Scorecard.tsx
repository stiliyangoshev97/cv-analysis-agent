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
import { useSendNotification } from '../hooks';

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
  
  const { mutate: sendNotification, isPending: isSending } = useSendNotification();

  const handleSendEmail = () => {
    sendNotification({ cvId: result.id, channel: 'email' });
  };

  const handleSendWhatsApp = () => {
    sendNotification({ cvId: result.id, channel: 'whatsapp' });
  };

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
      <CardFooter className="px-6 py-4 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-700 flex flex-wrap gap-2 justify-between mt-0">
        <div className="flex gap-2">
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
          <Button
            variant="outline"
            size="sm"
            onClick={handleSendEmail}
            disabled={isSending}
            className="gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Email
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSendWhatsApp}
            disabled={isSending}
            className="gap-2"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
            WhatsApp
          </Button>
        </div>
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
