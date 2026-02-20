/**
 * @fileoverview Notification History Page Component.
 *
 * Displays a paginated list of sent notifications with filtering options.
 * Allows users to view history, resend failed notifications, and delete entries.
 *
 * @module features/notification/pages/NotificationHistoryPage
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  Badge,
  Text,
  Select,
  Spinner,
} from '@/shared/components';
import {
  useNotificationHistory,
  useNotificationStats,
  useResendNotification,
  useDeleteNotification,
} from '../hooks';
import type { NotificationType, NotificationStatus } from '@/shared/types';

/**
 * Format relative time from ISO string.
 */
const formatRelativeTime = (isoString: string): string => {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
};

/**
 * Get badge variant for notification status.
 */
const getStatusBadge = (status: NotificationStatus) => {
  switch (status) {
    case 'sent':
      return <Badge variant="success">Sent</Badge>;
    case 'failed':
      return <Badge variant="error">Failed</Badge>;
    case 'pending':
      return <Badge variant="warning">Pending</Badge>;
    default:
      return <Badge>{status}</Badge>;
  }
};

/**
 * Get icon for notification type.
 */
const getTypeIcon = (type: NotificationType) => {
  return type === 'email' ? '📧' : '💬';
};

/**
 * Notification History Page Component.
 *
 * @example
 * ```tsx
 * <NotificationHistoryPage />
 * ```
 */
export const NotificationHistoryPage = () => {
  // Filters
  const [typeFilter, setTypeFilter] = useState<NotificationType | ''>('');
  const [statusFilter, setStatusFilter] = useState<NotificationStatus | ''>('');
  const [currentPage, setCurrentPage] = useState(0);
  const limit = 10;

  // Queries
  const { data: history, isLoading } = useNotificationHistory({
    type: typeFilter || undefined,
    status: statusFilter || undefined,
    limit,
    offset: currentPage * limit,
  });
  const { data: stats } = useNotificationStats();

  // Mutations
  const { mutate: resend, isPending: isResending } = useResendNotification();
  const { mutate: remove, isPending: isDeleting } = useDeleteNotification();

  // Filter options
  const typeOptions = [
    { value: '', label: 'All Types' },
    { value: 'email', label: '📧 Email' },
    { value: 'whatsapp', label: '💬 WhatsApp' },
  ];

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'sent', label: '✓ Sent' },
    { value: 'failed', label: '✗ Failed' },
    { value: 'pending', label: '⏳ Pending' },
  ];

  return (
    <Container size="lg" className="py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Notification History
          </h1>
          <Link to="/settings/notifications">
            <Button variant="outline" size="sm">
              ← Back to Settings
            </Button>
          </Link>
        </div>
        <Text color="muted">
          View all notifications sent from the CV Screening Agent.
        </Text>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card padding="sm">
            <CardContent>
              <Text size="sm" color="muted">Total</Text>
              <Text size="lg" weight="semibold">{stats.total}</Text>
            </CardContent>
          </Card>
          <Card padding="sm">
            <CardContent>
              <Text size="sm" color="muted">Sent</Text>
              <Text size="lg" weight="semibold" className="text-green-600 dark:text-green-400">
                {stats.sent}
              </Text>
            </CardContent>
          </Card>
          <Card padding="sm">
            <CardContent>
              <Text size="sm" color="muted">Failed</Text>
              <Text size="lg" weight="semibold" className="text-red-600 dark:text-red-400">
                {stats.failed}
              </Text>
            </CardContent>
          </Card>
          <Card padding="sm">
            <CardContent>
              <Text size="sm" color="muted">Pending</Text>
              <Text size="lg" weight="semibold" className="text-yellow-600 dark:text-yellow-400">
                {stats.pending}
              </Text>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card padding="md" className="mb-6">
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Select
                label="Type"
                options={typeOptions}
                value={typeFilter}
                onChange={(e) => {
                  setTypeFilter(e.target.value as NotificationType | '');
                  setCurrentPage(0);
                }}
              />
            </div>
            <div className="flex-1">
              <Select
                label="Status"
                options={statusOptions}
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value as NotificationStatus | '');
                  setCurrentPage(0);
                }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* History List */}
      <Card padding="md">
        <CardHeader>
          <CardTitle className="text-lg">
            Notifications {history && `(${history.total})`}
          </CardTitle>
          <CardDescription>
            {statusFilter === 'failed' && 'Click "Resend" to retry failed notifications.'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner size="lg" />
            </div>
          ) : !history || history.items.length === 0 ? (
            <div className="text-center py-12">
              <Text size="lg" className="mb-2">📭</Text>
              <Text color="muted">
                {typeFilter || statusFilter
                  ? 'No notifications match your filters.'
                  : 'No notifications sent yet.'}
              </Text>
            </div>
          ) : (
            <div className="space-y-3">
              {history.items.map((notification) => (
                <div
                  key={notification.id}
                  className="flex flex-col sm:flex-row sm:items-start gap-3 sm:gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-700"
                >
                  {/* Top row on mobile: Icon + Status + Time */}
                  <div className="flex items-start gap-3 sm:contents">
                    {/* Type Icon */}
                    <div className="text-2xl flex-shrink-0">{getTypeIcon(notification.type)}</div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        {getStatusBadge(notification.status)}
                        <Text size="sm" color="muted" className="whitespace-nowrap">
                          {formatRelativeTime(notification.created_at)}
                        </Text>
                      </div>
                      <Text weight="medium" className="truncate mb-1">
                        {notification.candidate_name || 'Unknown Candidate'}
                        {notification.cv_score !== null && notification.cv_score !== undefined && (
                          <span className="text-gray-500 dark:text-gray-400 ml-2">
                            Score: {notification.cv_score}%
                          </span>
                        )}
                      </Text>
                      <Text size="sm" color="muted" className="truncate">
                        To: {notification.recipient}
                      </Text>
                      {notification.error_message && (
                        <Text size="sm" className="text-red-600 dark:text-red-400 mt-1 break-words">
                          Error: {notification.error_message}
                        </Text>
                      )}
                    </div>
                  </div>

                  {/* Actions - full width on mobile */}
                  <div className="flex items-center gap-2 sm:flex-shrink-0 ml-auto sm:ml-0">
                    {notification.status === 'failed' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => resend(notification.id)}
                        disabled={isResending}
                        className="text-xs sm:text-sm"
                      >
                        {isResending ? '...' : 'Resend'}
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        if (confirm('Delete this notification from history?')) {
                          remove(notification.id);
                        }
                      }}
                      disabled={isDeleting}
                      className="text-gray-500 hover:text-red-600"
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {history && history.total > limit && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
              <Text size="sm" color="muted">
                Showing {currentPage * limit + 1}-
                {Math.min((currentPage + 1) * limit, history.total)} of {history.total}
              </Text>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
                  disabled={currentPage === 0}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((p) => p + 1)}
                  disabled={!history.has_more}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default NotificationHistoryPage;
