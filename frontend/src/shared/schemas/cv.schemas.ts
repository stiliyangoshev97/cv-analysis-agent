/**
 * @fileoverview Core Zod schemas for CV evaluation responses.
 *
 * These schemas define the data contracts between frontend and backend.
 * Types are inferred from schemas - single source of truth pattern.
 *
 * @module schemas/cv.schemas
 * @see {@link https://zod.dev/ Zod Documentation}
 */

import { z } from 'zod';

// =============================================================================
// Enums
// =============================================================================

/**
 * Pass/Fail status enum for CV evaluation results.
 *
 * @example
 * ```typescript
 * const status: PassFailStatus = 'pass';
 * passFailStatusSchema.parse(status); // ✅ Valid
 * ```
 */
export const passFailStatusSchema = z.enum(['pass', 'fail']);

// =============================================================================
// Evaluation Schemas
// =============================================================================

/**
 * Individual evaluation criterion schema.
 *
 * Represents a single criterion with its pass/fail status and reasoning.
 * 
 * Current criteria evaluated:
 * - Education (High School+)
 * - Fintech Experience
 * - Technical Skills (TypeScript/Python)
 * - Soft Skills & Adaptability (fast learner, stress, teamwork)
 * - AI-Native Development (AI tools, RAG, MCP, agents)
 *
 * @example
 * ```typescript
 * const criterion: EvaluationCriteria = {
 *   name: 'AI-Native Development',
 *   passed: true,
 *   details: "Uses GitHub Copilot, experience with LangChain agents"
 * };
 * ```
 */
export const evaluationCriteriaSchema = z.object({
  /** Name of the criterion being evaluated */
  name: z.string(),
  /** Whether the criterion was met */
  passed: z.boolean(),
  /** Detailed explanation of the evaluation */
  details: z.string(),
});

/**
 * CV evaluation response schema.
 *
 * This is the main output from Claude AI evaluation,
 * displayed on the frontend scorecard.
 *
 * @example
 * ```typescript
 * const evaluation: CVEvaluationResponse = {
 *   status: 'pass',
 *   match_score: 85,
 *   reasoning: 'Strong candidate with...',
 *   criteria: [...],
 *   candidate_name: 'John Doe'
 * };
 * ```
 */
export const cvEvaluationResponseSchema = z.object({
  /** Overall pass/fail status */
  status: passFailStatusSchema,
  /** Match score from 0-100 */
  match_score: z.number().min(0).max(100),
  /** Detailed reasoning paragraph */
  reasoning: z.string(),
  /** List of individual criteria evaluations */
  criteria: z.array(evaluationCriteriaSchema),
  /** Extracted candidate name, null if not found */
  candidate_name: z.string().nullable(),
});

// =============================================================================
// API Response Schemas
// =============================================================================

/**
 * Upload endpoint response schema.
 *
 * Wraps the CV evaluation with success status and message.
 *
 * @example
 * ```typescript
 * const response: UploadResponse = {
 *   success: true,
 *   message: 'CV evaluated successfully',
 *   evaluation: { ... }
 * };
 * ```
 */
export const uploadResponseSchema = z.object({
  /** Whether the upload/evaluation was successful */
  success: z.boolean(),
  /** Human-readable status message */
  message: z.string(),
  /** UUID of the uploaded CV (for chat, history, etc.) */
  cv_id: z.string().nullable(),
  /** Evaluation result, null on failure */
  evaluation: cvEvaluationResponseSchema.nullable(),
});

/**
 * Error response schema for API errors.
 */
export const errorResponseSchema = z.object({
  /** Always false for errors */
  success: z.literal(false),
  /** Error message */
  error: z.string(),
  /** Additional error details */
  detail: z.string().optional(),
});

// =============================================================================
// Frontend State Schemas
// =============================================================================

/**
 * Upload progress tracking schema.
 *
 * Used by Axios upload progress callback.
 */
export const uploadProgressSchema = z.object({
  /** Bytes uploaded so far */
  loaded: z.number(),
  /** Total bytes to upload */
  total: z.number(),
  /** Percentage complete (0-100) */
  percentage: z.number().min(0).max(100),
});

// =============================================================================
// CV List Schemas
// =============================================================================

/**
 * CV summary schema for list views.
 *
 * Lightweight representation of a CV for list/grid displays.
 */
export const cvSummarySchema = z.object({
  /** CV UUID */
  id: z.string().uuid(),
  /** Original uploaded filename */
  filename: z.string(),
  /** Extracted candidate name if available */
  candidate_name: z.string().nullable(),
  /** Processing status */
  status: z.string(),
  /** Upload timestamp ISO format */
  uploaded_at: z.string(),
  /** Latest evaluation score if available */
  score: z.number().nullable(),
  /** Pass/fail status if evaluated */
  evaluation_status: z.string().nullable(),
});

/**
 * CV list response schema.
 *
 * Paginated list of CV summaries.
 */
export const cvListResponseSchema = z.object({
  /** List of CV summaries */
  cvs: z.array(cvSummarySchema),
  /** Total number of CVs */
  total: z.number(),
  /** Page size */
  limit: z.number(),
  /** Items skipped */
  offset: z.number(),
});

/**
 * CV result schema for frontend state.
 *
 * Combines evaluation result with metadata for display.
 */
export const cvResultSchema = z.object({
  /** Unique identifier for this result */
  id: z.string(),
  /** Original filename */
  filename: z.string(),
  /** The evaluation response from API */
  evaluation: cvEvaluationResponseSchema,
  /** When the CV was uploaded */
  uploadedAt: z.date(),
});

// =============================================================================
// Inferred Types
// =============================================================================

/** Pass/Fail status type */
export type PassFailStatus = z.infer<typeof passFailStatusSchema>;

/** Individual evaluation criterion */
export type EvaluationCriteria = z.infer<typeof evaluationCriteriaSchema>;

/** Full CV evaluation response from API */
export type CVEvaluationResponse = z.infer<typeof cvEvaluationResponseSchema>;

/** Upload endpoint response */
export type UploadResponse = z.infer<typeof uploadResponseSchema>;

/** Error response from API */
export type ErrorResponse = z.infer<typeof errorResponseSchema>;

/** Upload progress tracking */
export type UploadProgress = z.infer<typeof uploadProgressSchema>;

/** CV summary for list views */
export type CVSummary = z.infer<typeof cvSummarySchema>;

/** CV list response */
export type CVListResponse = z.infer<typeof cvListResponseSchema>;

/** CV result for frontend state */
export type CVResult = z.infer<typeof cvResultSchema>;
