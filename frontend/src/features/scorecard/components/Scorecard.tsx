import { Badge, Button } from '../../../components/ui';
import type { CVResult } from '../../../types';
import { CriteriaItem } from './CriteriaItem';
import { ScoreRing } from './ScoreRing';

interface ScorecardProps {
  result: CVResult;
  onDismiss: (id: string) => void;
}

export const Scorecard = ({ result, onDismiss }: ScorecardProps) => {
  const { evaluation, filename } = result;
  const isPassed = evaluation.status === 'pass';

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
      {/* Header */}
      <div className={`px-6 py-4 ${isPassed ? 'bg-green-50 border-b border-green-100' : 'bg-red-50 border-b border-red-100'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isPassed ? 'bg-green-100' : 'bg-red-100'}`}>
              {isPassed ? (
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">
                {evaluation.candidate_name || 'Unknown Candidate'}
              </h3>
              <p className="text-sm text-gray-500">{filename}</p>
            </div>
          </div>
          <Badge variant={isPassed ? 'success' : 'error'} size="lg">
            {isPassed ? 'PASSED' : 'FAILED'}
          </Badge>
        </div>
      </div>

      {/* Body */}
      <div className="p-6">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Score Ring */}
          <div className="flex justify-center md:justify-start">
            <ScoreRing score={evaluation.match_score} />
          </div>

          {/* Reasoning */}
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">AI Assessment</h4>
            <p className="text-sm text-gray-600 leading-relaxed">{evaluation.reasoning}</p>
          </div>
        </div>

        {/* Criteria */}
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Evaluation Criteria</h4>
          <div className="space-y-2">
            {evaluation.criteria.map((criterion, index) => (
              <CriteriaItem key={index} criteria={criterion} />
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end">
        <Button variant="ghost" size="sm" onClick={() => onDismiss(result.id)}>
          Dismiss
        </Button>
      </div>
    </div>
  );
};
