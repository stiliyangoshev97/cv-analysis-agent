/**
 * @fileoverview Notification Settings Panel component.
 *
 * Main UI for managing notification preferences including:
 * - Email toggle with SMTP configuration (BYOK)
 * - WhatsApp toggle with Twilio configuration (BYOK)
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
  useClearSmtpConfig,
  useClearTwilioConfig,
} from '../hooks';
import type { NotificationChannel, SmtpConfigUpdate, TwilioConfigUpdate } from '@/shared/types';

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

const SettingsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
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

const ChevronDownIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

const ChevronUpIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
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
  const { mutate: clearSmtp, isPending: isClearingSmtp } = useClearSmtpConfig();
  const { mutate: clearTwilio, isPending: isClearingTwilio } = useClearTwilioConfig();

  // Local state for form
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [whatsappEnabled, setWhatsappEnabled] = useState(false);
  const [whatsappNumber, setWhatsappNumber] = useState('');
  const [threshold, setThreshold] = useState(70);
  const [hasChanges, setHasChanges] = useState(false);
  
  // SMTP configuration state (BYOK)
  const [showSmtpConfig, setShowSmtpConfig] = useState(false);
  const [smtpHost, setSmtpHost] = useState('');
  const [smtpPort, setSmtpPort] = useState('587');
  const [smtpUsername, setSmtpUsername] = useState('');
  const [smtpPassword, setSmtpPassword] = useState('');
  const [smtpFromEmail, setSmtpFromEmail] = useState('');
  const [smtpFromName, setSmtpFromName] = useState('CV Screening Agent');
  const [smtpUseTls, setSmtpUseTls] = useState(true);
  
  // Twilio configuration state (BYOK)
  const [showTwilioConfig, setShowTwilioConfig] = useState(false);
  const [twilioAccountSid, setTwilioAccountSid] = useState('');
  const [twilioAuthToken, setTwilioAuthToken] = useState('');
  const [twilioWhatsappFrom, setTwilioWhatsappFrom] = useState('');

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

  // Check if SMTP form has values
  const hasSmtpValues = smtpHost || smtpUsername || smtpPassword || smtpFromEmail;
  
  // Check if Twilio form has values
  const hasTwilioValues = twilioAccountSid || twilioAuthToken || twilioWhatsappFrom;

  // Save settings
  const handleSave = () => {
    const updateData: {
      email_enabled: boolean;
      whatsapp_enabled: boolean;
      whatsapp_number: string | null;
      threshold_score: number;
      smtp_config?: SmtpConfigUpdate;
      twilio_config?: TwilioConfigUpdate;
    } = {
      email_enabled: emailEnabled,
      whatsapp_enabled: whatsappEnabled,
      whatsapp_number: whatsappNumber || null,
      threshold_score: threshold,
    };
    
    // Include SMTP config if values are provided
    if (hasSmtpValues) {
      updateData.smtp_config = {
        host: smtpHost || null,
        port: parseInt(smtpPort) || 587,
        username: smtpUsername || null,
        password: smtpPassword || null,
        from_email: smtpFromEmail || null,
        from_name: smtpFromName || 'CV Screening Agent',
        use_tls: smtpUseTls,
      };
    }
    
    // Include Twilio config if values are provided
    if (hasTwilioValues) {
      updateData.twilio_config = {
        account_sid: twilioAccountSid || null,
        auth_token: twilioAuthToken || null,
        whatsapp_from: twilioWhatsappFrom || null,
      };
    }
    
    updateSettings(updateData);
    
    // Clear form fields after save (credentials are stored encrypted)
    setSmtpHost('');
    setSmtpPort('587');
    setSmtpUsername('');
    setSmtpPassword('');
    setSmtpFromEmail('');
    setSmtpFromName('CV Screening Agent');
    setTwilioAccountSid('');
    setTwilioAuthToken('');
    setTwilioWhatsappFrom('');
  };

  // Send test notification
  const handleTestNotification = (channel: NotificationChannel) => {
    resetTest();
    sendTest({ channel });
  };
  
  // Clear SMTP config
  const handleClearSmtp = () => {
    if (confirm('Are you sure you want to clear your SMTP configuration?')) {
      clearSmtp();
    }
  };
  
  // Clear Twilio config
  const handleClearTwilio = () => {
    if (confirm('Are you sure you want to clear your Twilio configuration?')) {
      clearTwilio();
    }
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

  // Determine configuration sources
  const emailSource = status?.email_source || 'none';
  const whatsappSource = status?.whatsapp_source || 'none';
  const smtpConfigured = settings?.smtp_config?.configured || false;
  const twilioConfigured = settings?.twilio_config?.configured || false;

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
                  {!status.email_configured && 'Email service is not configured. '}
                  {!status.whatsapp_configured && 'WhatsApp service is not configured. '}
                  You can configure your own credentials below.
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
              <Badge 
                variant={status?.email_configured ? 'success' : 'warning'} 
                size="sm"
                title={emailSource === 'user' ? 'Using your SMTP credentials' : emailSource === 'server' ? 'Using server configuration' : 'Not configured'}
              >
                {emailSource === 'user' ? 'BYOK' : emailSource === 'server' ? 'Server' : 'Not Configured'}
              </Badge>
              <Toggle
                checked={emailEnabled}
                onChange={setEmailEnabled}
                disabled={isUpdating || !status?.email_configured}
                label="Enable email notifications"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="border-t space-y-4">
          {/* SMTP Configuration Section */}
          <div className="space-y-3">
            <button
              type="button"
              onClick={() => setShowSmtpConfig(!showSmtpConfig)}
              className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              <SettingsIcon />
              <span>Configure SMTP (Bring Your Own)</span>
              {showSmtpConfig ? <ChevronUpIcon /> : <ChevronDownIcon />}
            </button>
            
            {showSmtpConfig && (
              <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
                {smtpConfigured && (
                  <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg mb-3">
                    <div>
                      <Text size="sm" className="font-medium text-green-800">SMTP Configured</Text>
                      <Text size="sm" className="text-green-700">
                        Host: {settings?.smtp_config?.host} • From: {settings?.smtp_config?.from_email_hint}
                      </Text>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearSmtp}
                      disabled={isClearingSmtp}
                      className="text-red-600 border-red-300 hover:bg-red-50"
                    >
                      {isClearingSmtp ? <Spinner size="sm" /> : 'Clear'}
                    </Button>
                  </div>
                )}
                
                <Text size="sm" className="text-gray-600">
                  {smtpConfigured 
                    ? 'Enter new credentials to update your SMTP configuration:'
                    : 'Enter your SMTP server credentials to send emails from your own account:'}
                </Text>
                
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="SMTP Host"
                    placeholder="smtp.gmail.com"
                    value={smtpHost}
                    onChange={(e) => setSmtpHost(e.target.value)}
                    disabled={isUpdating}
                  />
                  <Input
                    label="SMTP Port"
                    placeholder="587"
                    type="number"
                    value={smtpPort}
                    onChange={(e) => setSmtpPort(e.target.value)}
                    disabled={isUpdating}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="Username"
                    placeholder="your-email@gmail.com"
                    value={smtpUsername}
                    onChange={(e) => setSmtpUsername(e.target.value)}
                    disabled={isUpdating}
                  />
                  <Input
                    label="Password / App Password"
                    type="password"
                    placeholder="••••••••"
                    value={smtpPassword}
                    onChange={(e) => setSmtpPassword(e.target.value)}
                    disabled={isUpdating}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="From Email"
                    placeholder="notifications@yourcompany.com"
                    value={smtpFromEmail}
                    onChange={(e) => setSmtpFromEmail(e.target.value)}
                    disabled={isUpdating}
                  />
                  <Input
                    label="From Name"
                    placeholder="CV Screening Agent"
                    value={smtpFromName}
                    onChange={(e) => setSmtpFromName(e.target.value)}
                    disabled={isUpdating}
                  />
                </div>
                
                <div className="flex items-center gap-2">
                  <Toggle
                    checked={smtpUseTls}
                    onChange={setSmtpUseTls}
                    disabled={isUpdating}
                    label="Use TLS"
                  />
                  <Text size="sm" color="muted">Use TLS/STARTTLS encryption (recommended)</Text>
                </div>
              </div>
            )}
          </div>
          
          {emailEnabled && status?.email_configured && (
            <div className="flex items-center justify-between pt-3 border-t">
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
          )}
        </CardContent>
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
              <Badge 
                variant={status?.whatsapp_configured ? 'success' : 'warning'} 
                size="sm"
                title={whatsappSource === 'user' ? 'Using your Twilio credentials' : whatsappSource === 'server' ? 'Using server configuration' : 'Not configured'}
              >
                {whatsappSource === 'user' ? 'BYOK' : whatsappSource === 'server' ? 'Server' : 'Not Configured'}
              </Badge>
              <Toggle
                checked={whatsappEnabled}
                onChange={setWhatsappEnabled}
                disabled={isUpdating || !status?.whatsapp_configured}
                label="Enable WhatsApp notifications"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="border-t space-y-4">
          {/* Twilio Configuration Section */}
          <div className="space-y-3">
            <button
              type="button"
              onClick={() => setShowTwilioConfig(!showTwilioConfig)}
              className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              <SettingsIcon />
              <span>Configure Twilio (Bring Your Own)</span>
              {showTwilioConfig ? <ChevronUpIcon /> : <ChevronDownIcon />}
            </button>
            
            {showTwilioConfig && (
              <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
                {twilioConfigured && (
                  <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg mb-3">
                    <div>
                      <Text size="sm" className="font-medium text-green-800">Twilio Configured</Text>
                      <Text size="sm" className="text-green-700">
                        Account: ...{settings?.twilio_config?.account_sid_hint} • From: {settings?.twilio_config?.whatsapp_from_hint}
                      </Text>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearTwilio}
                      disabled={isClearingTwilio}
                      className="text-red-600 border-red-300 hover:bg-red-50"
                    >
                      {isClearingTwilio ? <Spinner size="sm" /> : 'Clear'}
                    </Button>
                  </div>
                )}
                
                <Text size="sm" className="text-gray-600">
                  {twilioConfigured 
                    ? 'Enter new credentials to update your Twilio configuration:'
                    : 'Enter your Twilio credentials to send WhatsApp messages from your own account:'}
                </Text>
                
                <Input
                  label="Account SID"
                  placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                  value={twilioAccountSid}
                  onChange={(e) => setTwilioAccountSid(e.target.value)}
                  disabled={isUpdating}
                />
                
                <Input
                  label="Auth Token"
                  type="password"
                  placeholder="••••••••••••••••••••••••••••••••"
                  value={twilioAuthToken}
                  onChange={(e) => setTwilioAuthToken(e.target.value)}
                  disabled={isUpdating}
                />
                
                <Input
                  label="WhatsApp Sender Number"
                  placeholder="+14155238886"
                  value={twilioWhatsappFrom}
                  onChange={(e) => setTwilioWhatsappFrom(e.target.value)}
                  helperText="Your Twilio WhatsApp-enabled phone number"
                  disabled={isUpdating}
                />
              </div>
            )}
          </div>
          
          {(whatsappEnabled || status?.whatsapp_configured) && (
            <div className="space-y-4 pt-3 border-t">
              <Input
                label="Your WhatsApp Number"
                placeholder="+1234567890"
                value={whatsappNumber}
                onChange={(e) => setWhatsappNumber(e.target.value)}
                helperText="Include country code (e.g., +1 for US)"
                disabled={isUpdating}
              />
              {whatsappEnabled && status?.whatsapp_configured && (
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
              )}
            </div>
          )}
        </CardContent>
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
          disabled={(!hasChanges && !hasSmtpValues && !hasTwilioValues) || isUpdating}
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
