/**
 * @fileoverview useSendNotification Hook
 *
 * React hook for sending manual CV notifications.
 * Uses TanStack Query for mutation handling.
 *
 * @module features/cv/hooks/useSendNotification
 *
 * @example
 * ```tsx
 * const { mutate: notify, isPending } = useSendNotification();
 * 
 * const handleNotify = (cvId: string, channel: 'email' | 'whatsapp') => {
 *   notify({ cvId, channel }, {
 *     onSuccess: () => console.log('Notification sent'),
 *   });
 * };
 * ```
 */

import { useMutation } from '@tanstack/react-query';
import { toast } from '@/shared/components/ui';
import { sendManualNotification } from '../api';

/**
 * Input for sending a manual notification.
 */
interface SendNotificationInput {
  /** The CV ID to send notification for */
  cvId: string;
  /** The notification channel */
  channel: 'email' | 'whatsapp';
}

/**
 * Hook to send manual CV notifications.
 *
 * Sends an email or WhatsApp notification for a CV evaluation.
 *
 * @returns Mutation for sending notifications
 *
 * @example
 * ```tsx
 * const { mutate: notify, isPending } = useSendNotification();
 * notify({ cvId: 'uuid', channel: 'email' });
 * ```
 */
export const useSendNotification = () => {
  return useMutation({
    mutationFn: ({ cvId, channel }: SendNotificationInput) => 
      sendManualNotification(cvId, channel),
    onSuccess: (data) => {
      if (data.success) {
        const channelLabel = data.channel === 'email' ? 'Email' : 'WhatsApp';
        toast.success(`${channelLabel} sent`, data.message);
      } else {
        toast.error('Notification failed', data.message);
      }
    },
    onError: (error: Error) => {
      toast.error('Failed to send notification', error.message);
    },
  });
};
