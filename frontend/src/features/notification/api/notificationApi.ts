/**
 * @fileoverview Notification API functions.
 *
 * Provides functions for all notification-related API calls:
 * - Get notification settings
 * - Update notification settings
 * - Send test notifications
 * - Get service status
 * - Clear SMTP/Twilio configuration (BYOK)
 *
 * @module features/notification/api
 */

import { apiClient } from '@/shared/api';
import type {
  NotificationSettings,
  NotificationSettingsUpdate,
  NotificationChannel,
  NotificationResult,
  NotificationServiceStatus,
} from '@/shared/types';

/**
 * Get current user's notification settings.
 *
 * @returns Promise resolving to notification settings
 *
 * @example
 * ```typescript
 * const settings = await getNotificationSettings();
 * console.log(`Email enabled: ${settings.email_enabled}`);
 * ```
 */
export const getNotificationSettings = async (): Promise<NotificationSettings> => {
  const response = await apiClient.get<NotificationSettings>('/api/notifications/');
  return response.data;
};

/**
 * Update user's notification settings.
 *
 * @param data - Settings to update (partial)
 * @returns Promise resolving to updated settings
 *
 * @example
 * ```typescript
 * const updated = await updateNotificationSettings({
 *   email_enabled: true,
 *   threshold_score: 75
 * });
 * ```
 */
export const updateNotificationSettings = async (
  data: NotificationSettingsUpdate
): Promise<NotificationSettings> => {
  const response = await apiClient.put<NotificationSettings>('/api/notifications/', data);
  return response.data;
};

/**
 * Send a test notification to a specific channel.
 *
 * @param channel - 'email' or 'whatsapp'
 * @param params - Optional override for recipient
 * @returns Promise resolving to notification result
 *
 * @example
 * ```typescript
 * const result = await sendTestNotification('email');
 * if (result.success) {
 *   console.log('Test email sent!');
 * }
 * ```
 */
export const sendTestNotification = async (
  channel: NotificationChannel,
  params?: { to_email?: string; to_number?: string }
): Promise<NotificationResult> => {
  const response = await apiClient.post<NotificationResult>(
    `/api/notifications/test/${channel}`,
    params || {}
  );
  return response.data;
};

/**
 * Get notification service configuration status.
 *
 * @returns Promise resolving to service status
 *
 * @example
 * ```typescript
 * const status = await getNotificationStatus();
 * if (!status.email_configured) {
 *   console.log('Email not configured on server');
 * }
 * ```
 */
export const getNotificationStatus = async (): Promise<NotificationServiceStatus> => {
  const response = await apiClient.get<NotificationServiceStatus>('/api/notifications/status');
  return response.data;
};

/**
 * Clear user's SMTP configuration (BYOK).
 *
 * @returns Promise resolving to success message
 *
 * @example
 * ```typescript
 * await clearSmtpConfig();
 * ```
 */
export const clearSmtpConfig = async (): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    '/api/notifications/smtp-config'
  );
  return response.data;
};

/**
 * Clear user's Twilio configuration (BYOK).
 *
 * @returns Promise resolving to success message
 *
 * @example
 * ```typescript
 * await clearTwilioConfig();
 * ```
 */
export const clearTwilioConfig = async (): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    '/api/notifications/twilio-config'
  );
  return response.data;
};
