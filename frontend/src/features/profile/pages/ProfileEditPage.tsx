/**
 * @fileoverview Profile Edit Page.
 *
 * Page for editing a profile and its criteria.
 *
 * @module features/profile/pages/ProfileEditPage
 */

import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Heading,
  Text,
  Button,
  Card,
  Input,
  Textarea,
  Spinner,
} from '@/shared/components/ui';
import {
  useProfile,
  useUpdateProfile,
  useAddCriterion,
  useUpdateCriterion,
  useDeleteCriterion,
} from '../hooks';
import { CriterionCard, CriterionForm } from '../components';
import type { CriterionCreate, CriterionResponse, CriterionUpdate } from '@/shared/schemas';

/**
 * Profile Edit Page
 *
 * Allows editing profile metadata and managing criteria.
 */
export const ProfileEditPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: profile, isLoading, error } = useProfile(id!);

  // Mutations
  const updateProfile = useUpdateProfile();
  const addCriterion = useAddCriterion();
  const updateCriterion = useUpdateCriterion();
  const deleteCriterion = useDeleteCriterion();

  // Local form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [passingScore, setPassingScore] = useState(60);
  const [minCriteria, setMinCriteria] = useState(3);
  const [isEditing, setIsEditing] = useState(false);

  // Criterion editing state
  const [showCriterionForm, setShowCriterionForm] = useState(false);
  const [editingCriterion, setEditingCriterion] = useState<CriterionResponse | null>(null);

  // Initialize form when profile loads
  if (profile && !isEditing && name === '') {
    setName(profile.name);
    setDescription(profile.description ?? '');
    setPassingScore(profile.passing_score);
    setMinCriteria(profile.minimum_criteria_met);
    setIsEditing(true);
  }

  if (isLoading) {
    return (
      <Container>
        <div className="flex justify-center items-center py-20">
          <Spinner size="lg" />
        </div>
      </Container>
    );
  }

  if (error || !profile) {
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
          <Text color="muted">Profile not found</Text>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => navigate('/profiles')}
          >
            Back to Profiles
          </Button>
        </Card>
      </Container>
    );
  }

  // Check if user can edit
  if (profile.is_system_template) {
    return (
      <Container>
        <Card className="p-8 text-center">
          <svg
            className="w-12 h-12 mx-auto text-yellow-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 15v2m0 0v2m0-2h2m-2 0H10m4-6a4 4 0 11-8 0 4 4 0 018 0z"
            />
          </svg>
          <Text>System templates cannot be edited</Text>
          <Text size="sm" color="muted" className="mt-1">
            Clone this template to create your own editable version.
          </Text>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => navigate(`/profiles/${id}`)}
          >
            View Profile
          </Button>
        </Card>
      </Container>
    );
  }

  const handleSaveProfile = () => {
    updateProfile.mutate({
      id: profile.id,
      data: {
        name: name.trim(),
        description: description.trim() || null,
        passing_score: passingScore,
        minimum_criteria_met: minCriteria,
      },
    });
  };

  const handleAddCriterion = (data: CriterionCreate) => {
    addCriterion.mutate(
      { profileId: profile.id, data },
      {
        onSuccess: () => {
          setShowCriterionForm(false);
        },
      }
    );
  };

  const handleUpdateCriterion = (data: CriterionCreate) => {
    if (!editingCriterion) return;

    const updateData: CriterionUpdate = {
      name: data.name,
      description: data.description,
      max_points: data.max_points,
      keywords: data.keywords,
      evaluation_guidelines: data.evaluation_guidelines,
      is_required: data.is_required,
      sort_order: data.sort_order,
    };

    updateCriterion.mutate(
      {
        profileId: profile.id,
        criterionId: editingCriterion.id,
        data: updateData,
      },
      {
        onSuccess: () => {
          setEditingCriterion(null);
        },
      }
    );
  };

  const handleDeleteCriterion = (criterionId: string) => {
    if (confirm('Are you sure you want to delete this criterion?')) {
      deleteCriterion.mutate({
        profileId: profile.id,
        criterionId,
      });
    }
  };

  const hasChanges =
    name !== profile.name ||
    description !== (profile.description ?? '') ||
    passingScore !== profile.passing_score ||
    minCriteria !== profile.minimum_criteria_met;

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
          <li>
            <Link
              to={`/profiles/${profile.id}`}
              className="hover:text-blue-600 dark:hover:text-blue-400"
            >
              {profile.name}
            </Link>
          </li>
          <li>/</li>
          <li className="text-gray-900 dark:text-white">Edit</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Heading level={1}>Edit Profile</Heading>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            onClick={() => navigate(`/profiles/${profile.id}`)}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSaveProfile}
            disabled={!hasChanges || updateProfile.isPending}
            isLoading={updateProfile.isPending}
          >
            Save Changes
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
              Profile Name
            </label>
            <Input
              id="profile-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Senior Backend Developer"
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
              max={profile.criteria.length}
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
          <Heading level={2}>Criteria</Heading>
          <Button
            onClick={() => {
              setEditingCriterion(null);
              setShowCriterionForm(true);
            }}
            disabled={showCriterionForm || !!editingCriterion}
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
              isSubmitting={addCriterion.isPending}
              mode="create"
            />
          )}

          {/* Existing Criteria */}
          {profile.criteria
            .sort((a, b) => a.sort_order - b.sort_order)
            .map((criterion) =>
              editingCriterion?.id === criterion.id ? (
                <CriterionForm
                  key={criterion.id}
                  criterion={criterion}
                  onSubmit={handleUpdateCriterion}
                  onCancel={() => setEditingCriterion(null)}
                  isSubmitting={updateCriterion.isPending}
                  mode="edit"
                />
              ) : (
                <CriterionCard
                  key={criterion.id}
                  criterion={criterion}
                  isEditable
                  onEdit={() => setEditingCriterion(criterion)}
                  onDelete={() => handleDeleteCriterion(criterion.id)}
                />
              )
            )}

          {/* Empty State */}
          {profile.criteria.length === 0 && !showCriterionForm && (
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
