/**
 * @fileoverview Profile React Query hooks.
 *
 * Provides hooks for fetching and mutating profile data.
 *
 * @module features/profile/hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/shared/components/ui';
import {
  getProfiles,
  getProfile,
  createProfile,
  updateProfile,
  deleteProfile,
  cloneProfile,
  addCriterion,
  updateCriterion,
  deleteCriterion,
} from '../api';
import type {
  ProfileCreate,
  ProfileUpdate,
  CriterionCreate,
  CriterionUpdate,
  CloneProfileRequest,
} from '@/shared/schemas';

// =============================================================================
// Query Keys
// =============================================================================

/** Query keys for profiles */
export const profileKeys = {
  all: ['profiles'] as const,
  lists: () => [...profileKeys.all, 'list'] as const,
  list: () => [...profileKeys.lists()] as const,
  details: () => [...profileKeys.all, 'detail'] as const,
  detail: (id: string) => [...profileKeys.details(), id] as const,
};

// =============================================================================
// Profile Query Hooks
// =============================================================================

/**
 * Hook to fetch all profiles.
 *
 * @returns Query result with profile list
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useProfiles();
 * ```
 */
export const useProfiles = () => {
  return useQuery({
    queryKey: profileKeys.list(),
    queryFn: getProfiles,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

/**
 * Hook to fetch a single profile.
 *
 * @param id - Profile UUID
 * @returns Query result with full profile
 *
 * @example
 * ```tsx
 * const { data: profile } = useProfile('uuid');
 * ```
 */
export const useProfile = (id: string) => {
  return useQuery({
    queryKey: profileKeys.detail(id),
    queryFn: () => getProfile(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};

// =============================================================================
// Profile Mutation Hooks
// =============================================================================

/**
 * Hook to create a new profile.
 *
 * @returns Mutation for creating profiles
 *
 * @example
 * ```tsx
 * const { mutate: create } = useCreateProfile();
 * create({ name: 'Dev', criteria: [...] });
 * ```
 */
export const useCreateProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ProfileCreate) => createProfile(data),
    onSuccess: (profile) => {
      queryClient.invalidateQueries({ queryKey: profileKeys.lists() });
      toast.success('Profile created', `"${profile.name}" is ready to use.`);
    },
    onError: (error: Error) => {
      toast.error('Failed to create profile', error.message);
    },
  });
};

/**
 * Hook to update a profile.
 *
 * @returns Mutation for updating profiles
 *
 * @example
 * ```tsx
 * const { mutate: update } = useUpdateProfile();
 * update({ id: 'uuid', data: { passing_score: 75 } });
 * ```
 */
export const useUpdateProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProfileUpdate }) =>
      updateProfile(id, data),
    onSuccess: (profile) => {
      queryClient.invalidateQueries({ queryKey: profileKeys.lists() });
      queryClient.invalidateQueries({ queryKey: profileKeys.detail(profile.id) });
      toast.success('Profile updated');
    },
    onError: (error: Error) => {
      toast.error('Failed to update profile', error.message);
    },
  });
};

/**
 * Hook to delete a profile.
 *
 * @returns Mutation for deleting profiles
 *
 * @example
 * ```tsx
 * const { mutate: remove } = useDeleteProfile();
 * remove('uuid');
 * ```
 */
export const useDeleteProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteProfile(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: profileKeys.lists() });
      queryClient.removeQueries({ queryKey: profileKeys.detail(id) });
      toast.success('Profile deleted');
    },
    onError: (error: Error) => {
      toast.error('Failed to delete profile', error.message);
    },
  });
};

/**
 * Hook to clone a profile.
 *
 * @returns Mutation for cloning profiles
 *
 * @example
 * ```tsx
 * const { mutate: clone } = useCloneProfile();
 * clone({ id: 'uuid', data: { new_name: 'My Copy' } });
 * ```
 */
export const useCloneProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CloneProfileRequest }) =>
      cloneProfile(id, data),
    onSuccess: (profile) => {
      queryClient.invalidateQueries({ queryKey: profileKeys.lists() });
      toast.success('Profile cloned', `Created "${profile.name}".`);
    },
    onError: (error: Error) => {
      toast.error('Failed to clone profile', error.message);
    },
  });
};

// =============================================================================
// Criterion Mutation Hooks
// =============================================================================

/**
 * Hook to add a criterion to a profile.
 *
 * @returns Mutation for adding criteria
 */
export const useAddCriterion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: CriterionCreate }) =>
      addCriterion(profileId, data),
    onSuccess: (_, { profileId }) => {
      queryClient.invalidateQueries({ queryKey: profileKeys.detail(profileId) });
      toast.success('Criterion added');
    },
    onError: (error: Error) => {
      toast.error('Failed to add criterion', error.message);
    },
  });
};

/**
 * Hook to update a criterion.
 *
 * @returns Mutation for updating criteria
 */
export const useUpdateCriterion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      profileId,
      criterionId,
      data,
    }: {
      profileId: string;
      criterionId: string;
      data: CriterionUpdate;
    }) => updateCriterion(profileId, criterionId, data),
    onSuccess: (_, { profileId }) => {
      queryClient.invalidateQueries({ queryKey: profileKeys.detail(profileId) });
      toast.success('Criterion updated');
    },
    onError: (error: Error) => {
      toast.error('Failed to update criterion', error.message);
    },
  });
};

/**
 * Hook to delete a criterion.
 *
 * @returns Mutation for deleting criteria
 */
export const useDeleteCriterion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ profileId, criterionId }: { profileId: string; criterionId: string }) =>
      deleteCriterion(profileId, criterionId),
    onSuccess: (_, { profileId }) => {
      queryClient.invalidateQueries({ queryKey: profileKeys.detail(profileId) });
      toast.success('Criterion deleted');
    },
    onError: (error: Error) => {
      toast.error('Failed to delete criterion', error.message);
    },
  });
};
