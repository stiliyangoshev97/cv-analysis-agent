/**
 * @fileoverview Notification Settings Page component.
 *
 * Full-page view for notification settings.
 *
 * @module features/notification/pages/NotificationSettingsPage
 */

import { Container } from '@/shared/components';
import { NotificationSettingsPanel } from '../components';

/**
 * Notification Settings Page.
 *
 * @example
 * ```tsx
 * <NotificationSettingsPage />
 * ```
 */
export const NotificationSettingsPage = () => {
  return (
    <Container size="md" className="py-8">
      <NotificationSettingsPanel />
    </Container>
  );
};
