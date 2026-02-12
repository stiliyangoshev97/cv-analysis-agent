/**
 * @fileoverview Auth feature module.
 *
 * Provides authentication functionality including login, register, and Google OAuth.
 *
 * @module features/auth
 */

// Store
export { useAuthStore } from './store';

// Hooks
export { useRegister, useLogin, useGoogleAuth, useLogout, useAuthState } from './hooks';

// Components
export { LoginForm, RegisterForm, AuthPage, UserMenu, ProtectedRoute } from './components';

// Pages (re-exports for consistency)
export { AuthPage as AuthPageView } from './pages';

// API
export * as authApi from './api';
