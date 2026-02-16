/**
 * @fileoverview Notification-related Zod schemas.
 *
 * Defines validation schemas for notification settings and API responses.
 * Supports BYOK (Bring Your Own Keys) for SMTP and Twilio credentials.
 *
 * @module schemas/notification
 */

import { z } from 'zod';

// =============================================================================
// SMTP Configuration (BYOK)
// =============================================================================

/**
 * Schema for SMTP configuration update request.
 */
export const smtpConfigUpdateSchema = z.object({
  host: z.string().max(255).nullable().optional(),
  port: z.number().min(1).max(65535).optional().default(587),
  username: z.string().max(255).nullable().optional(),
  password: z.string().max(500).nullable().optional(),
  from_email: z.string().email().max(255).nullable().optional(),
  from_name: z.string().max(100).optional().default('CV Screening Agent'),
  use_tls: z.boolean().optional().default(true),
});

export type SmtpConfigUpdate = z.infer<typeof smtpConfigUpdateSchema>;

/**
 * Schema for SMTP configuration response (credentials masked).
 */
export const smtpConfigResponseSchema = z.object({
  configured: z.boolean(),
  host: z.string().nullable().optional(),
  port: z.number().nullable().optional(),
  from_email_hint: z.string().nullable().optional(),
  from_name: z.string().nullable().optional(),
  use_tls: z.boolean().optional(),
});

export type SmtpConfigResponse = z.infer<typeof smtpConfigResponseSchema>;

// =============================================================================
// Twilio Configuration (BYOK)
// =============================================================================

/**
 * Schema for Twilio configuration update request.
 */
export const twilioConfigUpdateSchema = z.object({
  account_sid: z.string().max(100).nullable().optional(),
  auth_token: z.string().max(100).nullable().optional(),
  whatsapp_from: z.string().max(20).nullable().optional(),
});

export type TwilioConfigUpdate = z.infer<typeof twilioConfigUpdateSchema>;

/**
 * Schema for Twilio configuration response (credentials masked).
 */
export const twilioConfigResponseSchema = z.object({
  configured: z.boolean(),
  account_sid_hint: z.string().nullable().optional(),
  whatsapp_from_hint: z.string().nullable().optional(),
});

export type TwilioConfigResponse = z.infer<typeof twilioConfigResponseSchema>;

// =============================================================================
// Notification Settings
// =============================================================================

/**
 * Schema for notification settings response from API.
 */
export const notificationSettingsSchema = z.object({
  email_enabled: z.boolean(),
  whatsapp_enabled: z.boolean(),
  whatsapp_number: z.string().nullable(),
  threshold_score: z.number().min(0).max(100),
  smtp_config: smtpConfigResponseSchema.optional(),
  twilio_config: twilioConfigResponseSchema.optional(),
});

/**
 * Type for notification settings.
 */
export type NotificationSettings = z.infer<typeof notificationSettingsSchema>;

/**
 * Schema for updating notification settings.
 */
export const notificationSettingsUpdateSchema = z.object({
  email_enabled: z.boolean().optional(),
  whatsapp_enabled: z.boolean().optional(),
  whatsapp_number: z.string().nullable().optional(),
  threshold_score: z.number().min(0).max(100).optional(),
  smtp_config: smtpConfigUpdateSchema.optional(),
  twilio_config: twilioConfigUpdateSchema.optional(),
});

/**
 * Type for notification settings update request.
 */
export type NotificationSettingsUpdate = z.infer<typeof notificationSettingsUpdateSchema>;

// =============================================================================
// Test Notification
// =============================================================================

/**
 * Notification channel enum.
 */
export const notificationChannelSchema = z.enum(['email', 'whatsapp']);
export type NotificationChannel = z.infer<typeof notificationChannelSchema>;

/**
 * Schema for test notification request.
 */
export const sendTestNotificationRequestSchema = z.object({
  to_email: z.string().email().optional(),
  to_number: z.string().optional(),
});

export type SendTestNotificationRequest = z.infer<typeof sendTestNotificationRequestSchema>;

/**
 * Schema for notification result response.
 */
export const notificationResultSchema = z.object({
  success: z.boolean(),
  channel: notificationChannelSchema,
  message: z.string(),
  message_id: z.string().optional().nullable(),
  error: z.string().optional().nullable(),
});

export type NotificationResult = z.infer<typeof notificationResultSchema>;

// =============================================================================
// Service Status
// =============================================================================

/**
 * Schema for notification service status.
 */
export const notificationServiceStatusSchema = z.object({
  email_configured: z.boolean(),
  whatsapp_configured: z.boolean(),
  email_source: z.enum(['user', 'server', 'none']).optional(),
  whatsapp_source: z.enum(['user', 'server', 'none']).optional(),
  email_service: z.string(),
  whatsapp_service: z.string(),
});

export type NotificationServiceStatus = z.infer<typeof notificationServiceStatusSchema>;
