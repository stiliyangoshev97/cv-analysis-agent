/**
 * @fileoverview Notification feature module.
 *
 * Provides notification settings functionality including:
 * - Email/WhatsApp toggle settings
 * - Threshold configuration
 * - Test notification sending
 *
 * @module features/notification
 */

// Components
export { NotificationSettingsPanel, Toggle, ThresholdSlider } from './components';

// Pages
export { NotificationSettingsPage } from './pages';

// Hooks
export {
  useNotificationSettings,
  useUpdateNotificationSettings,
  useSendTestNotification,
  useNotificationStatus,
} from './hooks';

// API
export * as notificationApi from './api';
