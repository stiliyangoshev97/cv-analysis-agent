/**
 * @fileoverview Notification-related Zod schemas.
 *
 * Defines validation schemas for notification settings and API responses.
 *
 * @module schemas/notification
 */

import { z } from 'zod';

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
  email_service: z.string(),
  whatsapp_service: z.string(),
});

export type NotificationServiceStatus = z.infer<typeof notificationServiceStatusSchema>;
