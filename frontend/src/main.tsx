/**
 * @fileoverview Application entry point.
 *
 * Sets up React root with providers.
 *
 * @module main
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryProvider } from '@/providers';
import { ToastProvider, PageErrorBoundary } from '@/shared/components/ui';
import './index.css';
import App from './App';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PageErrorBoundary>
      <QueryProvider>
        <App />
        <ToastProvider />
      </QueryProvider>
    </PageErrorBoundary>
  </StrictMode>,
);
