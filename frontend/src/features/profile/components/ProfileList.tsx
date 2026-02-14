/**
 * @fileoverview Profile List Component.
 *
 * Displays a grid of profile cards with filtering.
 *
 * @module features/profile/components/ProfileList
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { ProfileSummary } from '@/shared/schemas';
import { Text, Spinner, Input } from '@/shared/components/ui';
import { ProfileCard } from './ProfileCard';

interface ProfileListProps {
  /** List of profiles to display */
  profiles: ProfileSummary[];
  /** Loading state */
  isLoading?: boolean;
  /** Called when clone button is clicked */
  onClone?: (profile: ProfileSummary) => void;
  /** Called when delete button is clicked */
  onDelete?: (profile: ProfileSummary) => void;
}

/**
 * Profile List Component
 *
 * Displays profiles in a grid with search filtering.
 *
 * @example
 * ```tsx
 * <ProfileList
 *   profiles={data?.profiles ?? []}
 *   isLoading={isLoading}
 *   onClone={handleClone}
 *   onDelete={handleDelete}
 * />
 * ```
 */
export const ProfileList = ({
  profiles,
  isLoading,
  onClone,
  onDelete,
}: ProfileListProps) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  // Filter profiles by search query
  const filteredProfiles = profiles.filter((profile) =>
    profile.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    profile.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Separate system and user profiles
  const systemProfiles = filteredProfiles.filter((p) => p.is_system_template);
  const userProfiles = filteredProfiles.filter((p) => !p.is_system_template);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="max-w-md">
        <Input
          type="search"
          placeholder="Search profiles..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full"
        />
      </div>

      {/* Empty State */}
      {filteredProfiles.length === 0 && (
        <div className="text-center py-12">
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
          <Text color="muted">
            {searchQuery ? 'No profiles match your search' : 'No profiles found'}
          </Text>
        </div>
      )}

      {/* User Profiles */}
      {userProfiles.length > 0 && (
        <div>
          <Text weight="medium" className="mb-3 text-gray-700 dark:text-gray-300">
            My Profiles ({userProfiles.length})
          </Text>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {userProfiles.map((profile) => (
              <ProfileCard
                key={profile.id}
                profile={profile}
                onClick={() => navigate(`/profiles/${profile.id}`)}
                onEdit={() => navigate(`/profiles/${profile.id}/edit`)}
                onClone={() => onClone?.(profile)}
                onDelete={() => onDelete?.(profile)}
              />
            ))}
          </div>
        </div>
      )}

      {/* System Templates */}
      {systemProfiles.length > 0 && (
        <div>
          <Text weight="medium" className="mb-3 text-gray-700 dark:text-gray-300">
            System Templates ({systemProfiles.length})
          </Text>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemProfiles.map((profile) => (
              <ProfileCard
                key={profile.id}
                profile={profile}
                onClick={() => navigate(`/profiles/${profile.id}`)}
                onClone={() => onClone?.(profile)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
