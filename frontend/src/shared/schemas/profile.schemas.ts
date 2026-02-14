/**
 * @fileoverview Zod schemas for profile/template API.
 *
 * Defines validation schemas and TypeScript types for evaluation profiles.
 *
 * @module shared/schemas/profile.schemas
 */

import { z } from 'zod';

// =============================================================================
// Criterion Schemas
// =============================================================================

/**
 * Schema for creating a criterion.
 */
export const criterionCreateSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional().nullable(),
  max_points: z.number().int().min(1).max(100),
  keywords: z.array(z.string()).optional().default([]),
  evaluation_guidelines: z.string().optional().nullable(),
  is_required: z.boolean().optional().default(false),
  sort_order: z.number().int().min(0).optional().default(0),
});
export type CriterionCreate = z.infer<typeof criterionCreateSchema>;

/**
 * Schema for updating a criterion.
 */
export const criterionUpdateSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().optional().nullable(),
  max_points: z.number().int().min(1).max(100).optional(),
  keywords: z.array(z.string()).optional(),
  evaluation_guidelines: z.string().optional().nullable(),
  is_required: z.boolean().optional(),
  sort_order: z.number().int().min(0).optional(),
});
export type CriterionUpdate = z.infer<typeof criterionUpdateSchema>;

/**
 * Schema for criterion response.
 */
export const criterionResponseSchema = z.object({
  id: z.string().uuid(),
  template_id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  max_points: z.number(),
  keywords: z.array(z.string()),
  evaluation_guidelines: z.string().nullable(),
  is_required: z.boolean(),
  sort_order: z.number(),
});
export type CriterionResponse = z.infer<typeof criterionResponseSchema>;

// =============================================================================
// Profile Schemas
// =============================================================================

/**
 * Schema for creating a profile with criteria.
 */
export const profileCreateSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional().nullable(),
  passing_score: z.number().int().min(0).max(100).optional().default(60),
  minimum_criteria_met: z.number().int().min(0).optional().default(3),
  criteria: z.array(criterionCreateSchema).min(1),
});
export type ProfileCreate = z.infer<typeof profileCreateSchema>;

/**
 * Schema for updating a profile.
 */
export const profileUpdateSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().optional().nullable(),
  passing_score: z.number().int().min(0).max(100).optional(),
  minimum_criteria_met: z.number().int().min(0).optional(),
});
export type ProfileUpdate = z.infer<typeof profileUpdateSchema>;

/**
 * Schema for profile summary (list view).
 */
export const profileSummarySchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  is_system_template: z.boolean(),
  passing_score: z.number(),
  criteria_count: z.number(),
});
export type ProfileSummary = z.infer<typeof profileSummarySchema>;

/**
 * Schema for full profile response.
 */
export const profileResponseSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  passing_score: z.number(),
  minimum_criteria_met: z.number(),
  user_id: z.string().uuid().nullable(),
  is_system_template: z.boolean(),
  criteria: z.array(criterionResponseSchema),
});
export type ProfileResponse = z.infer<typeof profileResponseSchema>;

/**
 * Schema for profile list response.
 */
export const profileListResponseSchema = z.object({
  profiles: z.array(profileSummarySchema),
  total: z.number(),
});
export type ProfileListResponse = z.infer<typeof profileListResponseSchema>;

/**
 * Schema for clone profile request.
 */
export const cloneProfileRequestSchema = z.object({
  new_name: z.string().min(1).max(100),
  description: z.string().optional().nullable(),
});
export type CloneProfileRequest = z.infer<typeof cloneProfileRequestSchema>;
