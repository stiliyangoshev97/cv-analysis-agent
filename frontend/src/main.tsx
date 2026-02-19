/**
 * @fileoverview Application entry point.
 *
 * Sets up React root with providers.
 *
 * @module main
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { QueryProvider } from '@/providers';
import { ToastProvider, PageErrorBoundary } from '@/shared/components/ui';
import './index.css';
import App from './App';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PageErrorBoundary>
      <GoogleOAuthProvider clientId={googleClientId}>
        <QueryProvider>
          <App />
          <ToastProvider />
        </QueryProvider>
      </GoogleOAuthProvider>
    </PageErrorBoundary>
  </StrictMode>,
);
