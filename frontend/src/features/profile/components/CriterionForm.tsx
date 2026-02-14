/**
 * @fileoverview Criterion Form Component.
 *
 * Form for creating or editing a criterion.
 *
 * @module features/profile/components/CriterionForm
 */

import { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Input,
  Textarea,
  Text,
  Badge,
} from '@/shared/components/ui';
import type { CriterionCreate, CriterionResponse } from '@/shared/schemas';

interface CriterionFormProps {
  /** Existing criterion data (for edit mode) */
  criterion?: CriterionResponse | CriterionCreate;
  /** Called when form is submitted */
  onSubmit: (data: CriterionCreate) => void;
  /** Called when form is cancelled */
  onCancel: () => void;
  /** Whether form is submitting */
  isSubmitting?: boolean;
  /** Form mode */
  mode?: 'create' | 'edit';
}

/**
 * Criterion Form
 *
 * Form for adding or editing evaluation criteria.
 *
 * @example
 * ```tsx
 * <CriterionForm
 *   onSubmit={handleAddCriterion}
 *   onCancel={() => setShowForm(false)}
 * />
 * ```
 */
export const CriterionForm = ({
  criterion,
  onSubmit,
  onCancel,
  isSubmitting = false,
  mode = 'create',
}: CriterionFormProps) => {
  const [name, setName] = useState(criterion?.name ?? '');
  const [description, setDescription] = useState(criterion?.description ?? '');
  const [maxPoints, setMaxPoints] = useState(criterion?.max_points ?? 10);
  const [keywords, setKeywords] = useState<string[]>(criterion?.keywords ?? []);
  const [keywordInput, setKeywordInput] = useState('');
  const [guidelines, setGuidelines] = useState(
    criterion?.evaluation_guidelines ?? ''
  );
  const [isRequired, setIsRequired] = useState(criterion?.is_required ?? false);

  // Reset form when criterion changes
  useEffect(() => {
    if (criterion) {
      setName(criterion.name);
      setDescription(criterion.description ?? '');
      setMaxPoints(criterion.max_points);
      setKeywords(criterion.keywords ?? []);
      setGuidelines(criterion.evaluation_guidelines ?? '');
      setIsRequired(criterion.is_required ?? false);
    }
  }, [criterion]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
      max_points: maxPoints,
      keywords,
      evaluation_guidelines: guidelines.trim() || null,
      is_required: isRequired,
      sort_order: 0, // Will be set by backend
    });
  };

  const handleAddKeyword = () => {
    const keyword = keywordInput.trim().toLowerCase();
    if (keyword && !keywords.includes(keyword)) {
      setKeywords([...keywords, keyword]);
      setKeywordInput('');
    }
  };

  const handleKeywordKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddKeyword();
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    setKeywords(keywords.filter((k) => k !== keyword));
  };

  return (
    <Card variant="outlined" className="p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between">
          <Text weight="semibold" className="text-gray-900 dark:text-white">
            {mode === 'create' ? 'Add Criterion' : 'Edit Criterion'}
          </Text>
        </div>

        {/* Name */}
        <div>
          <label
            htmlFor="criterion-name"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Name <span className="text-red-500">*</span>
          </label>
          <Input
            id="criterion-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Python Experience, Cloud Infrastructure, Leadership Skills"
            required
            autoFocus
          />
          <Text size="sm" color="muted" className="mt-1">
            The skill or qualification you want to evaluate
          </Text>
        </div>

        {/* Description */}
        <div>
          <label
            htmlFor="criterion-description"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Description
          </label>
          <Textarea
            id="criterion-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., Evaluate the candidate's proficiency in Python programming, including experience with web frameworks (Django, FastAPI), data processing, and writing clean, maintainable code."
            rows={2}
          />
          <Text size="sm" color="muted" className="mt-1">
            Detailed description of what the AI should look for
          </Text>
        </div>

        {/* Max Points & Required */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="criterion-points"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Max Points <span className="text-red-500">*</span>
            </label>
            <Input
              id="criterion-points"
              type="number"
              min={1}
              max={100}
              value={maxPoints}
              onChange={(e) => setMaxPoints(parseInt(e.target.value) || 1)}
              required
            />
          </div>
          <div className="flex items-center pt-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isRequired}
                onChange={(e) => setIsRequired(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Required criterion
              </span>
            </label>
          </div>
        </div>

        {/* Keywords */}
        <div>
          <label
            htmlFor="criterion-keywords"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Keywords
          </label>
          <div className="flex gap-2">
            <Input
              id="criterion-keywords"
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyDown={handleKeywordKeyDown}
              placeholder="e.g., python, django, fastapi, flask"
              className="flex-1"
            />
            <Button
              type="button"
              variant="secondary"
              onClick={handleAddKeyword}
              disabled={!keywordInput.trim()}
            >
              Add
            </Button>
          </div>
          {keywords.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {keywords.map((keyword) => (
                <Badge
                  key={keyword}
                  variant="neutral"
                  className="pr-1.5 flex items-center gap-1"
                >
                  {keyword}
                  <button
                    type="button"
                    onClick={() => handleRemoveKeyword(keyword)}
                    className="ml-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    aria-label={`Remove ${keyword}`}
                  >
                    ×
                  </button>
                </Badge>
              ))}
            </div>
          )}
          <Text size="sm" color="muted" className="mt-1">
            Keywords help the AI identify relevant sections in CVs. Press Enter or click Add after each keyword.
          </Text>
        </div>

        {/* Evaluation Guidelines */}
        <div>
          <label
            htmlFor="criterion-guidelines"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Evaluation Guidelines
          </label>
          <Textarea
            id="criterion-guidelines"
            value={guidelines}
            onChange={(e) => setGuidelines(e.target.value)}
            placeholder="e.g., Award full points (20) for 5+ years of Python experience with production projects. Award 15 points for 3-5 years. Award 10 points for 1-3 years with strong portfolio. Award 5 points for basic knowledge or bootcamp completion. Award 0 points if no Python experience mentioned."
            rows={4}
          />
          <Text size="sm" color="muted" className="mt-1">
            Specific scoring instructions for the AI. Be clear about what earns full, partial, or no points.
          </Text>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="ghost"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            isLoading={isSubmitting}
            disabled={!name.trim() || isSubmitting}
          >
            {mode === 'create' ? 'Add Criterion' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Card>
  );
};
