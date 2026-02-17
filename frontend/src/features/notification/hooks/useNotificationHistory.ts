/**
 * @fileoverview React Query hooks for notification history.
 *
 * Provides hooks for fetching and mutating notification history data.
 *
 * @module features/notification/hooks/useNotificationHistory
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  getNotificationHistory,
  getNotificationStats,
  getNotificationById,
  resendNotification,
  deleteNotification,
} from '../api/notificationApi';
import type { NotificationHistoryParams } from '@/shared/types';

/** Query key factory for notification history */
export const notificationHistoryKeys = {
  all: ['notification-history'] as const,
  list: (params?: NotificationHistoryParams) => [...notificationHistoryKeys.all, 'list', params] as const,
  stats: () => [...notificationHistoryKeys.all, 'stats'] as const,
  detail: (id: string) => [...notificationHistoryKeys.all, 'detail', id] as const,
};

/**
 * Hook to fetch notification history with filtering.
 *
 * @param params - Filter and pagination options
 * @returns Query result with notification history
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useNotificationHistory({ status: 'failed' });
 * ```
 */
export const useNotificationHistory = (params?: NotificationHistoryParams) => {
  return useQuery({
    queryKey: notificationHistoryKeys.list(params),
    queryFn: () => getNotificationHistory(params),
  });
};

/**
 * Hook to fetch notification statistics.
 *
 * @returns Query result with notification stats
 *
 * @example
 * ```tsx
 * const { data: stats } = useNotificationStats();
 * ```
 */
export const useNotificationStats = () => {
  return useQuery({
    queryKey: notificationHistoryKeys.stats(),
    queryFn: getNotificationStats,
  });
};

/**
 * Hook to fetch a single notification by ID.
 *
 * @param notificationId - UUID of the notification
 * @returns Query result with notification item
 */
export const useNotificationDetail = (notificationId: string) => {
  return useQuery({
    queryKey: notificationHistoryKeys.detail(notificationId),
    queryFn: () => getNotificationById(notificationId),
    enabled: !!notificationId,
  });
};

/**
 * Hook to resend a failed notification.
 *
 * @returns Mutation for resending notification
 *
 * @example
 * ```tsx
 * const { mutate: resend } = useResendNotification();
 * resend('notification-id');
 * ```
 */
export const useResendNotification = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: resendNotification,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Notification resent successfully');
      } else {
        toast.error(data.message || 'Failed to resend notification');
      }
      // Invalidate history to refresh the list
      queryClient.invalidateQueries({ queryKey: notificationHistoryKeys.all });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to resend notification');
    },
  });
};

/**
 * Hook to delete a notification from history.
 *
 * @returns Mutation for deleting notification
 *
 * @example
 * ```tsx
 * const { mutate: remove } = useDeleteNotification();
 * remove('notification-id');
 * ```
 */
export const useDeleteNotification = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteNotification,
    onSuccess: () => {
      toast.success('Notification deleted');
      // Invalidate history to refresh the list
      queryClient.invalidateQueries({ queryKey: notificationHistoryKeys.all });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete notification');
    },
  });
};
