/**
 * @fileoverview Notification Settings Panel component.
 *
 * Main UI for managing notification preferences including:
 * - Email toggle
 * - WhatsApp toggle with phone number input
 * - Threshold score slider
 * - Test notification buttons
 *
 * @module features/notification/components/NotificationSettingsPanel
 */

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent, Button, Input, Spinner, Text, Heading, Badge } from '@/shared/components';
import { Toggle } from './Toggle';
import { ThresholdSlider } from './ThresholdSlider';
import {
  useNotificationSettings,
  useUpdateNotificationSettings,
  useSendTestNotification,
  useNotificationStatus,
} from '../hooks';
import type { NotificationChannel } from '@/shared/types';

/**
 * Icon components for visual enhancement.
 */
const EmailIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);

const WhatsAppIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
);

const BellIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const XIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

/**
 * Notification Settings Panel component.
 *
 * @example
 * ```tsx
 * <NotificationSettingsPanel />
 * ```
 */
export const NotificationSettingsPanel = () => {
  const { data: settings, isLoading: settingsLoading, error: settingsError } = useNotificationSettings();
  const { data: status, isLoading: statusLoading } = useNotificationStatus();
  const { mutate: updateSettings, isPending: isUpdating } = useUpdateNotificationSettings();
  const { mutate: sendTest, isPending: isSendingTest, data: testResult, reset: resetTest } = useSendTestNotification();

  // Local state for form
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [whatsappEnabled, setWhatsappEnabled] = useState(false);
  const [whatsappNumber, setWhatsappNumber] = useState('');
  const [threshold, setThreshold] = useState(70);
  const [hasChanges, setHasChanges] = useState(false);

  // Sync local state with fetched settings
  useEffect(() => {
    if (settings) {
      setEmailEnabled(settings.email_enabled);
      setWhatsappEnabled(settings.whatsapp_enabled);
      setWhatsappNumber(settings.whatsapp_number || '');
      setThreshold(settings.threshold_score);
      setHasChanges(false);
    }
  }, [settings]);

  // Track changes
  useEffect(() => {
    if (settings) {
      const changed =
        emailEnabled !== settings.email_enabled ||
        whatsappEnabled !== settings.whatsapp_enabled ||
        whatsappNumber !== (settings.whatsapp_number || '') ||
        threshold !== settings.threshold_score;
      setHasChanges(changed);
    }
  }, [emailEnabled, whatsappEnabled, whatsappNumber, threshold, settings]);

  // Save settings
  const handleSave = () => {
    updateSettings({
      email_enabled: emailEnabled,
      whatsapp_enabled: whatsappEnabled,
      whatsapp_number: whatsappNumber || null,
      threshold_score: threshold,
    });
  };

  // Send test notification
  const handleTestNotification = (channel: NotificationChannel) => {
    resetTest();
    sendTest({ channel });
  };

  if (settingsLoading || statusLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (settingsError) {
    return (
      <Card variant="outlined">
        <CardContent className="py-8 text-center">
          <Text color="error">Failed to load notification settings</Text>
          <Text color="muted" size="sm" className="mt-2">
            {settingsError instanceof Error ? settingsError.message : 'Unknown error'}
          </Text>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-100 rounded-lg text-indigo-600">
          <BellIcon />
        </div>
        <div>
          <Heading level={2}>Notification Settings</Heading>
          <Text color="muted" size="sm">
            Configure how you want to be notified about CV evaluations
          </Text>
        </div>
      </div>

      {/* Service Status Banner */}
      {status && (!status.email_configured || !status.whatsapp_configured) && (
        <Card variant="outlined" className="border-yellow-200 bg-yellow-50">
          <CardContent className="py-3">
            <div className="flex items-start gap-3">
              <span className="text-yellow-600 mt-0.5">⚠️</span>
              <div>
                <Text className="font-medium text-yellow-800">Service Configuration</Text>
                <Text size="sm" className="text-yellow-700">
                  {!status.email_configured && 'Email service is not configured on the server. '}
                  {!status.whatsapp_configured && 'WhatsApp service is not configured on the server.'}
                </Text>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Threshold Setting */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            <Heading level={3}>Score Threshold</Heading>
          </div>
        </CardHeader>
        <CardContent>
          <Text color="muted" size="sm" className="mb-4">
            Only send notifications when a CV scores at or above this threshold
          </Text>
          <ThresholdSlider
            value={threshold}
            onChange={setThreshold}
            disabled={isUpdating}
          />
        </CardContent>
      </Card>

      {/* Email Notifications */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                <EmailIcon />
              </div>
              <div>
                <Heading level={3}>Email Notifications</Heading>
                <Text color="muted" size="sm">
                  Receive notifications via email
                </Text>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {status && (
                <Badge variant={status.email_configured ? 'success' : 'warning'} size="sm">
                  {status.email_configured ? 'Configured' : 'Not Configured'}
                </Badge>
              )}
              <Toggle
                checked={emailEnabled}
                onChange={setEmailEnabled}
                disabled={isUpdating || !status?.email_configured}
                label="Enable email notifications"
              />
            </div>
          </div>
        </CardHeader>
        {emailEnabled && status?.email_configured && (
          <CardContent className="border-t">
            <div className="flex items-center justify-between">
              <Text size="sm" color="muted">
                Notifications will be sent to your account email
              </Text>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleTestNotification('email')}
                disabled={isSendingTest || !emailEnabled}
              >
                {isSendingTest ? <Spinner size="sm" /> : 'Send Test Email'}
              </Button>
            </div>
          </CardContent>
        )}
      </Card>

      {/* WhatsApp Notifications */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg text-green-600">
                <WhatsAppIcon />
              </div>
              <div>
                <Heading level={3}>WhatsApp Notifications</Heading>
                <Text color="muted" size="sm">
                  Receive notifications via WhatsApp
                </Text>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {status && (
                <Badge variant={status.whatsapp_configured ? 'success' : 'warning'} size="sm">
                  {status.whatsapp_configured ? 'Configured' : 'Not Configured'}
                </Badge>
              )}
              <Toggle
                checked={whatsappEnabled}
                onChange={setWhatsappEnabled}
                disabled={isUpdating || !status?.whatsapp_configured}
                label="Enable WhatsApp notifications"
              />
            </div>
          </div>
        </CardHeader>
        {whatsappEnabled && status?.whatsapp_configured && (
          <CardContent className="border-t space-y-4">
            <Input
              label="WhatsApp Number"
              placeholder="+1234567890"
              value={whatsappNumber}
              onChange={(e) => setWhatsappNumber(e.target.value)}
              helperText="Include country code (e.g., +1 for US)"
              disabled={isUpdating}
            />
            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleTestNotification('whatsapp')}
                disabled={isSendingTest || !whatsappEnabled || !whatsappNumber}
              >
                {isSendingTest ? <Spinner size="sm" /> : 'Send Test Message'}
              </Button>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Test Result */}
      {testResult && (
        <Card variant="outlined" className={testResult.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <CardContent className="py-3">
            <div className="flex items-center gap-2">
              {testResult.success ? (
                <span className="text-green-600"><CheckIcon /></span>
              ) : (
                <span className="text-red-600"><XIcon /></span>
              )}
              <Text className={testResult.success ? 'text-green-800' : 'text-red-800'}>
                {testResult.message}
              </Text>
            </div>
            {testResult.error && (
              <Text size="sm" className="text-red-600 mt-1 ml-6">
                {testResult.error}
              </Text>
            )}
          </CardContent>
        </Card>
      )}

      {/* Save Button */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={!hasChanges || isUpdating}
        >
          {isUpdating ? (
            <>
              <Spinner size="sm" />
              <span className="ml-2">Saving...</span>
            </>
          ) : (
            'Save Changes'
          )}
        </Button>
      </div>
    </div>
  );
};
