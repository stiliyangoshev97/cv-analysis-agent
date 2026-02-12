/**
 * @fileoverview Barrel export for shared module.
 *
 * Central export point for all shared utilities, components,
 * schemas, types, hooks, and API client.
 *
 * @module shared
 *
 * @example
 * ```typescript
 * import { apiClient, Button, cn } from '@/shared';
 * import type { User, CVResult } from '@/shared';
 * ```
 */

// API Client
export * from './api';

// UI Components
export * from './components';

// Hooks
export * from './hooks';

// Zod Schemas and inferred types
export * from './schemas';

// Type re-exports
export * from './types';

// Utilities
export * from './utils';
