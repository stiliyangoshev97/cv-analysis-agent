/**
 * @fileoverview Chat-related Zod schemas.
 *
 * Defines validation schemas for RAG-powered CV chat functionality.
 *
 * @module schemas/chat
 */

import { z } from 'zod';

// =============================================================================
// Chat Message Schemas
// =============================================================================

/**
 * Schema for a chat message (user or assistant).
 */
export const chatMessageSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(['user', 'assistant']),
  content: z.string(),
  created_at: z.string().datetime(),
  sources: z.array(z.string()).default([]),
});
export type ChatMessage = z.infer<typeof chatMessageSchema>;

/**
 * Schema for chat message request.
 */
export const chatMessageRequestSchema = z.object({
  message: z.string().min(1).max(2000),
});
export type ChatMessageRequest = z.infer<typeof chatMessageRequestSchema>;

/**
 * Schema for ask question response.
 */
export const askResponseSchema = z.object({
  message: chatMessageSchema,
  sources_used: z.number().default(0),
});
export type AskResponse = z.infer<typeof askResponseSchema>;

/**
 * Schema for chat history response.
 */
export const chatHistoryResponseSchema = z.object({
  cv_id: z.string().uuid(),
  messages: z.array(chatMessageSchema),
  total: z.number(),
});
export type ChatHistoryResponse = z.infer<typeof chatHistoryResponseSchema>;

// =============================================================================
// Explain Criterion Schemas
// =============================================================================

/**
 * Schema for explain criterion request.
 */
export const explainCriterionRequestSchema = z.object({
  include_cv_evidence: z.boolean().default(true),
});
export type ExplainCriterionRequest = z.infer<typeof explainCriterionRequestSchema>;

/**
 * Schema for explain criterion response.
 */
export const explainCriterionResponseSchema = z.object({
  criterion: z.string(),
  score: z.number(),
  max_score: z.number(),
  explanation: z.string(),
  evidence: z.array(z.string()).default([]),
});
export type ExplainCriterionResponse = z.infer<typeof explainCriterionResponseSchema>;

// =============================================================================
// Compare CVs Schemas
// =============================================================================

/**
 * Schema for CV ranking item.
 */
export const cvRankingItemSchema = z.object({
  cv_id: z.string().uuid(),
  rank: z.number(),
  reason: z.string(),
});
export type CVRankingItem = z.infer<typeof cvRankingItemSchema>;

/**
 * Schema for compare CVs request.
 */
export const compareRequestSchema = z.object({
  cv_ids: z.array(z.string().uuid()).min(2).max(5),
  question: z.string().max(1000).default('Compare these candidates overall'),
});
export type CompareRequest = z.infer<typeof compareRequestSchema>;

/**
 * Schema for compare CVs response.
 */
export const compareResponseSchema = z.object({
  cv_ids: z.array(z.string().uuid()),
  comparison: z.string(),
  ranking: z.array(cvRankingItemSchema).nullable().default(null),
});
export type CompareResponse = z.infer<typeof compareResponseSchema>;
