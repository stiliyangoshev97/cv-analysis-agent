/**
 * @fileoverview Barrel export for UI components.
 *
 * All shared UI components use a variant-based approach with
 * class-variance-authority (CVA) for type-safe, consistent styling.
 *
 * @module shared/components/ui
 *
 * @example
 * ```tsx
 * import { Button, Card, Input, Badge } from '@/shared/components/ui';
 * ```
 */

// Buttons & Actions
export { Button } from './Button';

// Feedback & Status
export { Badge } from './Badge';
export { ProgressBar } from './ProgressBar';
export { Spinner } from './Spinner';
export { ToastProvider, toast } from './Toast';
export { ErrorBoundary, PageErrorBoundary, RouteErrorBoundary } from './ErrorBoundary';
export { ThemeToggle } from './ThemeToggle';

// Layout & Containers
export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './Card';
export { Container } from './Container';
export { Modal, ModalBody, ModalFooter } from './Modal';

// Typography
export { Text } from './Text';
export { Heading } from './Heading';

// Form Elements
export { Input } from './Input';
export { Textarea } from './Textarea';
export { Select } from './Select';
