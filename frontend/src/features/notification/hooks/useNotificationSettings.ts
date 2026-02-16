/**
 * @fileoverview Notification settings hooks.
 *
 * Provides React Query hooks for notification settings management.
 * Supports BYOK (Bring Your Own Keys) for SMTP and Twilio credentials.
 *
 * @module features/notification/hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getNotificationSettings,
  updateNotificationSettings,
  sendTestNotification,
  getNotificationStatus,
  clearSmtpConfig,
  clearTwilioConfig,
} from '../api';
import type { NotificationSettingsUpdate, NotificationChannel } from '@/shared/types';

/** Query key for notification settings */
const SETTINGS_KEY = ['notification-settings'];

/** Query key for notification service status */
const STATUS_KEY = ['notification-status'];

/**
 * Hook to fetch notification settings.
 *
 * @returns Query result with notification settings
 *
 * @example
 * ```tsx
 * const { data: settings, isLoading } = useNotificationSettings();
 * ```
 */
export const useNotificationSettings = () => {
  return useQuery({
    queryKey: SETTINGS_KEY,
    queryFn: getNotificationSettings,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

/**
 * Hook to update notification settings.
 *
 * Automatically invalidates the settings query on success.
 *
 * @returns Mutation for updating settings
 *
 * @example
 * ```tsx
 * const { mutate: updateSettings } = useUpdateNotificationSettings();
 * updateSettings({ email_enabled: true });
 * ```
 */
export const useUpdateNotificationSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: NotificationSettingsUpdate) => updateNotificationSettings(data),
    onSuccess: (data) => {
      queryClient.setQueryData(SETTINGS_KEY, data);
      // Also invalidate status since BYOK config may have changed
      queryClient.invalidateQueries({ queryKey: STATUS_KEY });
    },
  });
};

/**
 * Hook to send a test notification.
 *
 * @returns Mutation for sending test notifications
 *
 * @example
 * ```tsx
 * const { mutate: sendTest, isPending } = useSendTestNotification();
 * sendTest({ channel: 'email' });
 * ```
 */
export const useSendTestNotification = () => {
  return useMutation({
    mutationFn: ({ channel, params }: { 
      channel: NotificationChannel; 
      params?: { to_email?: string; to_number?: string } 
    }) => sendTestNotification(channel, params),
  });
};

/**
 * Hook to fetch notification service status.
 *
 * @returns Query result with service configuration status
 *
 * @example
 * ```tsx
 * const { data: status } = useNotificationStatus();
 * if (!status?.email_configured) {
 *   // Show warning
 * }
 * ```
 */
export const useNotificationStatus = () => {
  return useQuery({
    queryKey: STATUS_KEY,
    queryFn: getNotificationStatus,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
};

/**
 * Hook to clear SMTP configuration (BYOK).
 *
 * @returns Mutation for clearing SMTP config
 *
 * @example
 * ```tsx
 * const { mutate: clearSmtp } = useClearSmtpConfig();
 * clearSmtp();
 * ```
 */
export const useClearSmtpConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: clearSmtpConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEY });
      queryClient.invalidateQueries({ queryKey: STATUS_KEY });
    },
  });
};

/**
 * Hook to clear Twilio configuration (BYOK).
 *
 * @returns Mutation for clearing Twilio config
 *
 * @example
 * ```tsx
 * const { mutate: clearTwilio } = useClearTwilioConfig();
 * clearTwilio();
 * ```
 */
export const useClearTwilioConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: clearTwilioConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEY });
      queryClient.invalidateQueries({ queryKey: STATUS_KEY });
    },
  });
};
