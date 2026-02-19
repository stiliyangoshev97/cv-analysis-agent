/**
 * @fileoverview Profiles List Page.
 *
 * Main page showing all evaluation profiles.
 *
 * @module features/profile/pages/ProfilesPage
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Heading,
  Text,
  Button,
  Card,
} from '@/shared/components/ui';
import { useProfiles } from '../hooks';
import {
  ProfileList,
  CloneProfileModal,
  DeleteProfileModal,
} from '../components';
import type { ProfileSummary } from '@/shared/schemas';

/**
 * Profiles Page
 *
 * Displays list of all evaluation profiles with actions.
 */
export const ProfilesPage = () => {
  const navigate = useNavigate();
  const { data, isLoading, error } = useProfiles();

  // Modal state
  const [cloneProfile, setCloneProfile] = useState<ProfileSummary | null>(null);
  const [deleteProfile, setDeleteProfile] = useState<ProfileSummary | null>(null);

  if (error) {
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
          <Text color="muted">Failed to load profiles</Text>
          <Text size="sm" color="muted" className="mt-1">
            {error.message}
          </Text>
        </Card>
      </Container>
    );
  }

  return (
    <Container>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <Heading level={1} className="text-xl sm:text-2xl">Evaluation Profiles</Heading>
          <Text color="muted" size="sm" className="mt-1 sm:text-base">
            Manage your CV evaluation criteria templates
          </Text>
        </div>
        <Button onClick={() => navigate('/profiles/new')} className="w-full sm:w-auto">
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
          New Profile
        </Button>
      </div>

      {/* Profile List */}
      <ProfileList
        profiles={data?.profiles ?? []}
        isLoading={isLoading}
        onClone={setCloneProfile}
        onDelete={setDeleteProfile}
      />

      {/* Clone Modal */}
      <CloneProfileModal
        profile={cloneProfile}
        isOpen={!!cloneProfile}
        onClose={() => setCloneProfile(null)}
        onSuccess={(id) => navigate(`/profiles/${id}/edit`)}
      />

      {/* Delete Modal */}
      <DeleteProfileModal
        profile={deleteProfile}
        isOpen={!!deleteProfile}
        onClose={() => setDeleteProfile(null)}
      />
    </Container>
  );
};
