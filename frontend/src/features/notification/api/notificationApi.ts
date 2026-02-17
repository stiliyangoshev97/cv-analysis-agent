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
  NotificationHistoryList,
  NotificationHistoryItem,
  NotificationHistoryStats,
  NotificationHistoryParams,
  ResendNotificationResponse,
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

// =============================================================================
// Notification History API
// =============================================================================

/**
 * Get notification history with optional filtering.
 *
 * @param params - Filter and pagination options
 * @returns Promise resolving to paginated notification list
 *
 * @example
 * ```typescript
 * const history = await getNotificationHistory({ status: 'failed', limit: 10 });
 * console.log(`Found ${history.total} notifications`);
 * ```
 */
export const getNotificationHistory = async (
  params?: NotificationHistoryParams
): Promise<NotificationHistoryList> => {
  const queryParams = new URLSearchParams();
  if (params?.type) queryParams.append('type', params.type);
  if (params?.status) queryParams.append('status', params.status);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const query = queryParams.toString();
  const url = `/api/notifications/history${query ? `?${query}` : ''}`;
  const response = await apiClient.get<NotificationHistoryList>(url);
  return response.data;
};

/**
 * Get notification statistics.
 *
 * @returns Promise resolving to notification stats
 *
 * @example
 * ```typescript
 * const stats = await getNotificationStats();
 * console.log(`Sent: ${stats.sent}, Failed: ${stats.failed}`);
 * ```
 */
export const getNotificationStats = async (): Promise<NotificationHistoryStats> => {
  const response = await apiClient.get<NotificationHistoryStats>('/api/notifications/history/stats');
  return response.data;
};

/**
 * Get a single notification by ID.
 *
 * @param notificationId - UUID of the notification
 * @returns Promise resolving to notification item
 *
 * @example
 * ```typescript
 * const notification = await getNotificationById('123e4567-...');
 * ```
 */
export const getNotificationById = async (
  notificationId: string
): Promise<NotificationHistoryItem> => {
  const response = await apiClient.get<NotificationHistoryItem>(
    `/api/notifications/history/${notificationId}`
  );
  return response.data;
};

/**
 * Resend a failed notification.
 *
 * @param notificationId - UUID of the notification to resend
 * @returns Promise resolving to resend result
 *
 * @example
 * ```typescript
 * const result = await resendNotification('123e4567-...');
 * if (result.success) {
 *   console.log('Notification resent!');
 * }
 * ```
 */
export const resendNotification = async (
  notificationId: string
): Promise<ResendNotificationResponse> => {
  const response = await apiClient.post<ResendNotificationResponse>(
    `/api/notifications/history/${notificationId}/resend`
  );
  return response.data;
};

/**
 * Delete a notification from history.
 *
 * @param notificationId - UUID of the notification to delete
 * @returns Promise resolving to success message
 *
 * @example
 * ```typescript
 * await deleteNotification('123e4567-...');
 * ```
 */
export const deleteNotification = async (
  notificationId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    `/api/notifications/history/${notificationId}`
  );
  return response.data;
};
