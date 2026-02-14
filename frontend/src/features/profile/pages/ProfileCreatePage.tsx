/**
 * @fileoverview Profile Create Page.
 *
 * Page for creating a new profile with criteria.
 *
 * @module features/profile/pages/ProfileCreatePage
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Heading,
  Text,
  Button,
  Card,
  Input,
  Textarea,
} from '@/shared/components/ui';
import { useCreateProfile } from '../hooks';
import { CriterionForm, CriterionCard } from '../components';
import type { CriterionCreate, CriterionResponse } from '@/shared/schemas';

// Temporary ID generator for local criteria
let tempIdCounter = 0;
const generateTempId = () => `temp-${++tempIdCounter}`;

// Local criterion with temp ID
interface LocalCriterion extends CriterionCreate {
  tempId: string;
}

/**
 * Profile Create Page
 *
 * Allows creating a new profile with criteria.
 */
export const ProfileCreatePage = () => {
  const navigate = useNavigate();
  const createProfile = useCreateProfile();

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [passingScore, setPassingScore] = useState(60);
  const [minCriteria, setMinCriteria] = useState(3);
  const [criteria, setCriteria] = useState<LocalCriterion[]>([]);

  // Criterion form state
  const [showCriterionForm, setShowCriterionForm] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const handleAddCriterion = (data: CriterionCreate) => {
    setCriteria([...criteria, { ...data, tempId: generateTempId() }]);
    setShowCriterionForm(false);
  };

  const handleUpdateCriterion = (data: CriterionCreate) => {
    if (editingIndex === null) return;

    setCriteria(
      criteria.map((c, i) =>
        i === editingIndex ? { ...data, tempId: c.tempId } : c
      )
    );
    setEditingIndex(null);
  };

  const handleDeleteCriterion = (index: number) => {
    setCriteria(criteria.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (!name.trim() || criteria.length === 0) return;

    // Remove tempId for API
    const cleanCriteria: CriterionCreate[] = criteria.map(
      ({ tempId, ...rest }) => ({
        ...rest,
        sort_order: criteria.indexOf({ tempId, ...rest }),
      })
    );

    createProfile.mutate(
      {
        name: name.trim(),
        description: description.trim() || null,
        passing_score: passingScore,
        minimum_criteria_met: minCriteria,
        criteria: cleanCriteria,
      },
      {
        onSuccess: (profile) => {
          navigate(`/profiles/${profile.id}`);
        },
      }
    );
  };

  // Convert local criterion to CriterionResponse for display
  const toDisplayCriterion = (
    criterion: LocalCriterion,
    index: number
  ): CriterionResponse => ({
    id: criterion.tempId,
    template_id: 'temp',
    name: criterion.name,
    description: criterion.description ?? null,
    max_points: criterion.max_points,
    keywords: criterion.keywords ?? [],
    evaluation_guidelines: criterion.evaluation_guidelines ?? null,
    is_required: criterion.is_required ?? false,
    sort_order: index,
  });

  const canSubmit =
    name.trim() &&
    criteria.length > 0 &&
    !showCriterionForm &&
    editingIndex === null;

  return (
    <Container>
      {/* Breadcrumb */}
      <nav className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <li>
            <Link
              to="/profiles"
              className="hover:text-blue-600 dark:hover:text-blue-400"
            >
              Profiles
            </Link>
          </li>
          <li>/</li>
          <li className="text-gray-900 dark:text-white">New Profile</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Heading level={1}>Create Profile</Heading>
        <div className="flex items-center gap-2">
          <Button variant="ghost" onClick={() => navigate('/profiles')}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!canSubmit || createProfile.isPending}
            isLoading={createProfile.isPending}
          >
            Create Profile
          </Button>
        </div>
      </div>

      {/* Profile Metadata */}
      <Card className="p-6 mb-8">
        <Heading level={2} className="mb-4">
          Profile Settings
        </Heading>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <label
              htmlFor="profile-name"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Profile Name <span className="text-red-500">*</span>
            </label>
            <Input
              id="profile-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Senior Backend Developer"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label
              htmlFor="profile-description"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Description
            </label>
            <Textarea
              id="profile-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what this profile evaluates"
              rows={2}
            />
          </div>

          <div>
            <label
              htmlFor="passing-score"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Passing Score (%)
            </label>
            <Input
              id="passing-score"
              type="number"
              min={0}
              max={100}
              value={passingScore}
              onChange={(e) => setPassingScore(parseInt(e.target.value) || 0)}
            />
            <Text size="sm" color="muted" className="mt-1">
              Minimum percentage to pass evaluation
            </Text>
          </div>

          <div>
            <label
              htmlFor="min-criteria"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Minimum Criteria Met
            </label>
            <Input
              id="min-criteria"
              type="number"
              min={0}
              value={minCriteria}
              onChange={(e) => setMinCriteria(parseInt(e.target.value) || 0)}
            />
            <Text size="sm" color="muted" className="mt-1">
              Minimum number of criteria that must be satisfied
            </Text>
          </div>
        </div>
      </Card>

      {/* Criteria Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <Heading level={2}>Criteria</Heading>
            <Text size="sm" color="muted">
              Add at least one criterion to create the profile
            </Text>
          </div>
          <Button
            onClick={() => {
              setEditingIndex(null);
              setShowCriterionForm(true);
            }}
            disabled={showCriterionForm || editingIndex !== null}
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            Add Criterion
          </Button>
        </div>

        <div className="space-y-3">
          {/* New Criterion Form */}
          {showCriterionForm && (
            <CriterionForm
              onSubmit={handleAddCriterion}
              onCancel={() => setShowCriterionForm(false)}
              mode="create"
            />
          )}

          {/* Criteria List */}
          {criteria.map((criterion, index) =>
            editingIndex === index ? (
              <CriterionForm
                key={criterion.tempId}
                criterion={criterion}
                onSubmit={handleUpdateCriterion}
                onCancel={() => setEditingIndex(null)}
                mode="edit"
              />
            ) : (
              <CriterionCard
                key={criterion.tempId}
                criterion={toDisplayCriterion(criterion, index)}
                isEditable
                onEdit={() => setEditingIndex(index)}
                onDelete={() => handleDeleteCriterion(index)}
              />
            )
          )}

          {/* Empty State */}
          {criteria.length === 0 && !showCriterionForm && (
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
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              <Text color="muted" className="mb-4">
                No criteria added yet
              </Text>
              <Button
                onClick={() => setShowCriterionForm(true)}
                variant="secondary"
              >
                Add Your First Criterion
              </Button>
            </Card>
          )}
        </div>
      </div>
    </Container>
  );
};
