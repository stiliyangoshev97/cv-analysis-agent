/**
 * @fileoverview Profile API client functions.
 *
 * Handles all HTTP requests to the profile endpoints.
 *
 * @module features/profile/api
 */

import { apiClient } from '@/shared/api';
import type {
  ProfileListResponse,
  ProfileResponse,
  ProfileCreate,
  ProfileUpdate,
  CriterionCreate,
  CriterionUpdate,
  CriterionResponse,
  CloneProfileRequest,
} from '@/shared/schemas';

// =============================================================================
// Profile CRUD
// =============================================================================

/**
 * Fetch all profiles (system + user-created).
 *
 * @returns Promise with profile list
 *
 * @example
 * ```ts
 * const { profiles, total } = await getProfiles();
 * ```
 */
export const getProfiles = async (): Promise<ProfileListResponse> => {
  const response = await apiClient.get<ProfileListResponse>('/api/profiles/');
  return response.data;
};

/**
 * Fetch a single profile with all criteria.
 *
 * @param id - Profile UUID
 * @returns Promise with full profile
 *
 * @example
 * ```ts
 * const profile = await getProfile('uuid');
 * console.log(profile.criteria);
 * ```
 */
export const getProfile = async (id: string): Promise<ProfileResponse> => {
  const response = await apiClient.get<ProfileResponse>(`/api/profiles/${id}`);
  return response.data;
};

/**
 * Create a new profile with criteria.
 *
 * @param data - Profile creation data
 * @returns Promise with created profile
 *
 * @example
 * ```ts
 * const profile = await createProfile({
 *   name: 'Backend Developer',
 *   passing_score: 70,
 *   criteria: [{ name: 'Python', max_points: 20 }],
 * });
 * ```
 */
export const createProfile = async (data: ProfileCreate): Promise<ProfileResponse> => {
  const response = await apiClient.post<ProfileResponse>('/api/profiles/', data);
  return response.data;
};

/**
 * Update a profile's metadata (not criteria).
 *
 * @param id - Profile UUID
 * @param data - Fields to update
 * @returns Promise with updated profile
 *
 * @example
 * ```ts
 * const updated = await updateProfile('uuid', { passing_score: 75 });
 * ```
 */
export const updateProfile = async (
  id: string,
  data: ProfileUpdate
): Promise<ProfileResponse> => {
  const response = await apiClient.put<ProfileResponse>(`/api/profiles/${id}`, data);
  return response.data;
};

/**
 * Delete a user-created profile.
 *
 * @param id - Profile UUID
 *
 * @example
 * ```ts
 * await deleteProfile('uuid');
 * ```
 */
export const deleteProfile = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/profiles/${id}`);
};

/**
 * Clone a profile to create a custom copy.
 *
 * @param id - Source profile UUID
 * @param data - Clone request with new name
 * @returns Promise with cloned profile
 *
 * @example
 * ```ts
 * const cloned = await cloneProfile('uuid', { new_name: 'My Profile' });
 * ```
 */
export const cloneProfile = async (
  id: string,
  data: CloneProfileRequest
): Promise<ProfileResponse> => {
  const response = await apiClient.post<ProfileResponse>(
    `/api/profiles/${id}/clone`,
    data
  );
  return response.data;
};

// =============================================================================
// Criterion CRUD
// =============================================================================

/**
 * Add a criterion to a profile.
 *
 * @param profileId - Profile UUID
 * @param data - Criterion data
 * @returns Promise with created criterion
 *
 * @example
 * ```ts
 * const criterion = await addCriterion('profile-uuid', {
 *   name: 'SQL',
 *   max_points: 15,
 * });
 * ```
 */
export const addCriterion = async (
  profileId: string,
  data: CriterionCreate
): Promise<CriterionResponse> => {
  const response = await apiClient.post<CriterionResponse>(
    `/api/profiles/${profileId}/criteria`,
    data
  );
  return response.data;
};

/**
 * Update a criterion.
 *
 * @param profileId - Profile UUID
 * @param criterionId - Criterion UUID
 * @param data - Fields to update
 * @returns Promise with updated criterion
 *
 * @example
 * ```ts
 * const updated = await updateCriterion('profile-uuid', 'criterion-uuid', {
 *   max_points: 25,
 * });
 * ```
 */
export const updateCriterion = async (
  profileId: string,
  criterionId: string,
  data: CriterionUpdate
): Promise<CriterionResponse> => {
  const response = await apiClient.put<CriterionResponse>(
    `/api/profiles/${profileId}/criteria/${criterionId}`,
    data
  );
  return response.data;
};

/**
 * Delete a criterion from a profile.
 *
 * @param profileId - Profile UUID
 * @param criterionId - Criterion UUID
 *
 * @example
 * ```ts
 * await deleteCriterion('profile-uuid', 'criterion-uuid');
 * ```
 */
export const deleteCriterion = async (
  profileId: string,
  criterionId: string
): Promise<void> => {
  await apiClient.delete(`/api/profiles/${profileId}/criteria/${criterionId}`);
};
