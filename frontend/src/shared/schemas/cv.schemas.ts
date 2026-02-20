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
// Similarity & Search Schemas
// =============================================================================

/**
 * A CV found in similarity search.
 */
export const similarCVSchema = z.object({
  cv_id: z.string(),
  filename: z.string(),
  candidate_name: z.string().nullable(),
  similarity_score: z.number().min(0).max(1),
  evaluation_score: z.number().min(0).max(100).nullable(),
  status: z.string().nullable(),
});

/**
 * Response for finding similar CVs.
 */
export const similarCVsResponseSchema = z.object({
  source_cv_id: z.string(),
  similar_cvs: z.array(similarCVSchema),
  total: z.number(),
});

/**
 * CV ranking response schema.
 */
export const cvRankingResponseSchema = z.object({
  cv_id: z.string(),
  percentile: z.number().min(0).max(100),
  rank: z.number().min(1),
  total_cvs: z.number().min(1),
  evaluation_score: z.number().min(0).max(100),
  average_score: z.number().min(0).max(100),
  highest_score: z.number().min(0).max(100),
  label: z.string(),
});

/**
 * A single CV in a comparison.
 */
export const cvComparisonItemSchema = z.object({
  cv_id: z.string(),
  filename: z.string(),
  candidate_name: z.string().nullable(),
  evaluation_score: z.number().min(0).max(100).nullable(),
  status: z.string().nullable(),
  similarity_to_first: z.number().min(0).max(1),
});

/**
 * Request to compare multiple CVs.
 */
export const cvCompareRequestSchema = z.object({
  cv_ids: z.array(z.string()).min(2).max(10),
});

/**
 * Response for CV comparison.
 */
export const cvCompareResponseSchema = z.object({
  cvs: z.array(cvComparisonItemSchema),
  similarity_matrix: z.array(z.array(z.number())),
  best_match_id: z.string().nullable(),
  most_similar_pair: z.object({
    cv_id_1: z.string(),
    cv_id_2: z.string(),
    similarity: z.number(),
  }).nullable(),
});

/**
 * Request for semantic CV search.
 */
export const cvSearchRequestSchema = z.object({
  query: z.string().min(3).max(500),
  limit: z.number().min(1).max(50).default(10),
  min_similarity: z.number().min(0).max(1).default(0),
});

/**
 * Response for semantic CV search.
 */
export const cvSearchResponseSchema = z.object({
  query: z.string(),
  results: z.array(similarCVSchema),
  total: z.number(),
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

/** A CV found in similarity search */
export type SimilarCV = z.infer<typeof similarCVSchema>;

/** Response for finding similar CVs */
export type SimilarCVsResponse = z.infer<typeof similarCVsResponseSchema>;

/** CV ranking response */
export type CVRankingResponse = z.infer<typeof cvRankingResponseSchema>;

/** A single CV in a comparison */
export type CVComparisonItem = z.infer<typeof cvComparisonItemSchema>;

/** Request to compare CVs */
export type CVCompareRequest = z.infer<typeof cvCompareRequestSchema>;

/** Response for CV comparison */
export type CVCompareResponse = z.infer<typeof cvCompareResponseSchema>;

/** Request for semantic search */
export type CVSearchRequest = z.infer<typeof cvSearchRequestSchema>;

/** Response for semantic search */
export type CVSearchResponse = z.infer<typeof cvSearchResponseSchema>;
