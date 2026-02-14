/**
 * @fileoverview Profile Detail Page.
 *
 * Displays a single profile with all its criteria.
 *
 * @module features/profile/pages/ProfileDetailPage
 */

import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Heading,
  Text,
  Button,
  Card,
  Badge,
  Spinner,
} from '@/shared/components/ui';
import { useProfile } from '../hooks';
import {
  CriterionCard,
  CloneProfileModal,
  DeleteProfileModal,
} from '../components';
import type { ProfileSummary } from '@/shared/schemas';

/**
 * Profile Detail Page
 *
 * Shows full profile details including all criteria.
 */
export const ProfileDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: profile, isLoading, error } = useProfile(id!);

  // Modal state
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

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

  // Create summary for modals
  const profileSummary: ProfileSummary = {
    id: profile.id,
    name: profile.name,
    description: profile.description,
    is_system_template: profile.is_system_template,
    passing_score: profile.passing_score,
    criteria_count: profile.criteria.length,
  };

  // Calculate total max score
  const totalMaxScore = profile.criteria.reduce(
    (sum, c) => sum + c.max_points,
    0
  );

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
          <li className="text-gray-900 dark:text-white">{profile.name}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <Heading level={1}>{profile.name}</Heading>
            {profile.is_system_template && (
              <Badge variant="info" size="sm">
                System Template
              </Badge>
            )}
          </div>
          {profile.description && (
            <Text color="muted" className="mt-1">
              {profile.description}
            </Text>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!profile.is_system_template && (
            <Button
              variant="outline"
              onClick={() => navigate(`/profiles/${profile.id}/edit`)}
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Edit
            </Button>
          )}
          <Button variant="secondary" onClick={() => setShowCloneModal(true)}>
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            Clone
          </Button>
          {!profile.is_system_template && (
            <Button variant="danger" onClick={() => setShowDeleteModal(true)}>
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete
            </Button>
          )}
        </div>
      </div>

      {/* System Template Notice */}
      {profile.is_system_template && (
        <Card className="p-4 mb-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <Text weight="medium" className="text-blue-800 dark:text-blue-200">
                This is a system template
              </Text>
              <Text size="sm" className="text-blue-700 dark:text-blue-300 mt-1">
                System templates cannot be edited or deleted. Click <strong>Clone</strong> above to create your own editable copy of this template.
              </Text>
            </div>
          </div>
        </Card>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card className="p-4">
          <Text size="sm" color="muted">
            Criteria
          </Text>
          <Text size="lg" weight="semibold" className="text-gray-900 dark:text-white">
            {profile.criteria.length}
          </Text>
        </Card>
        <Card className="p-4">
          <Text size="sm" color="muted">
            Total Points
          </Text>
          <Text size="lg" weight="semibold" className="text-gray-900 dark:text-white">
            {totalMaxScore}
          </Text>
        </Card>
        <Card className="p-4">
          <Text size="sm" color="muted">
            Passing Score
          </Text>
          <Text size="lg" weight="semibold" className="text-gray-900 dark:text-white">
            {profile.passing_score}%
          </Text>
        </Card>
        <Card className="p-4">
          <Text size="sm" color="muted">
            Min. Criteria Met
          </Text>
          <Text size="lg" weight="semibold" className="text-gray-900 dark:text-white">
            {profile.minimum_criteria_met}
          </Text>
        </Card>
      </div>

      {/* Criteria List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <Heading level={2}>Criteria</Heading>
        </div>

        {profile.criteria.length === 0 ? (
          <Card className="p-8 text-center">
            <Text color="muted">No criteria defined</Text>
          </Card>
        ) : (
          <div className="space-y-3">
            {profile.criteria
              .sort((a, b) => a.sort_order - b.sort_order)
              .map((criterion) => (
                <CriterionCard
                  key={criterion.id}
                  criterion={criterion}
                  isEditable={false}
                />
              ))}
          </div>
        )}
      </div>

      {/* Clone Modal */}
      <CloneProfileModal
        profile={showCloneModal ? profileSummary : null}
        isOpen={showCloneModal}
        onClose={() => setShowCloneModal(false)}
        onSuccess={(newId) => navigate(`/profiles/${newId}/edit`)}
      />

      {/* Delete Modal */}
      <DeleteProfileModal
        profile={showDeleteModal ? profileSummary : null}
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onSuccess={() => navigate('/profiles')}
      />
    </Container>
  );
};
