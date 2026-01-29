import { Badge } from '../../../components/ui';
import type { EvaluationCriteria } from '../../../types';

interface CriteriaItemProps {
  criteria: EvaluationCriteria;
}

export const CriteriaItem = ({ criteria }: CriteriaItemProps) => {
  return (
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
          <h4 className="text-sm font-semibold text-gray-900">{criteria.name}</h4>
          <Badge variant={criteria.passed ? 'success' : 'error'} size="sm">
            {criteria.passed ? 'Passed' : 'Failed'}
          </Badge>
        </div>
        <p className="text-sm text-gray-600">{criteria.details}</p>
      </div>
    </div>
  );
};
