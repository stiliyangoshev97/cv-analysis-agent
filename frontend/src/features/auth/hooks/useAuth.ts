/**
 * @fileoverview Authentication hooks for React components.
 *
 * Provides TanStack Query mutations for auth operations
 * and a hook for accessing auth state.
 *
 * @module features/auth/hooks/useAuth
 *
 * @example
 * ```tsx
 * function LoginPage() {
 *   const { mutate: login, isPending } = useLogin();
 *   const { isAuthenticated } = useAuthState();
 *
 *   if (isAuthenticated) return <Navigate to="/dashboard" />;
 *
 *   return <LoginForm onSubmit={login} loading={isPending} />;
 * }
 * ```
 */

import { useMutation } from '@tanstack/react-query';
import { useAuthStore } from '../store';
import * as authApi from '../api';
import type { LoginRequest, RegisterRequest, GoogleAuthRequest } from '@/shared/types';

/**
 * Hook for user registration.
 *
 * Creates a new account and automatically logs in the user
 * by storing the returned tokens in the auth store.
 *
 * @returns TanStack Query mutation object
 *
 * @example
 * ```tsx
 * const { mutate: register, isPending, error } = useRegister();
 *
 * const handleSubmit = (data: RegisterRequest) => {
 *   register(data, {
 *     onSuccess: () => navigate('/dashboard'),
 *     onError: (err) => toast.error(err.message),
 *   });
 * };
 * ```
 */
export const useRegister = () => {
  const setAuth = useAuthStore((state) => state.setAuth);
  
  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      setAuth(response.user, response.tokens);
    },
  });
};

/**
 * Hook for user login.
 *
 * Authenticates the user and stores tokens in the auth store.
 *
 * @returns TanStack Query mutation object
 *
 * @example
 * ```tsx
 * const { mutate: login, isPending } = useLogin();
 *
 * <form onSubmit={() => login({ email, password })}>
 *   <button disabled={isPending}>
 *     {isPending ? 'Logging in...' : 'Login'}
 *   </button>
 * </form>
 * ```
 */
export const useLogin = () => {
  const setAuth = useAuthStore((state) => state.setAuth);
  
  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setAuth(response.user, response.tokens);
    },
  });
};

/**
 * Hook for Google OAuth authentication.
 *
 * Exchanges Google auth code for app tokens and stores them.
 *
 * @returns TanStack Query mutation object
 *
 * @example
 * ```tsx
 * const { mutate: googleAuth } = useGoogleAuth();
 *
 * const handleGoogleCallback = (code: string) => {
 *   googleAuth({
 *     code,
 *     redirect_uri: window.location.origin + '/auth/callback'
 *   });
 * };
 * ```
 */
export const useGoogleAuth = () => {
  const setAuth = useAuthStore((state) => state.setAuth);
  
  return useMutation({
    mutationFn: (data: GoogleAuthRequest) => authApi.googleAuth(data),
    onSuccess: (response) => {
      setAuth(response.user, response.tokens);
    },
  });
};

/**
 * Hook for user logout.
 *
 * Clears auth state from the store. Attempts to notify server
 * but will clear local state regardless of server response.
 *
 * @returns TanStack Query mutation object
 *
 * @example
 * ```tsx
 * const { mutate: logout } = useLogout();
 *
 * <button onClick={() => logout()}>Sign Out</button>
 * ```
 */
export const useLogout = () => {
  const logout = useAuthStore((state) => state.logout);
  const tokens = useAuthStore((state) => state.tokens);
  
  return useMutation({
    mutationFn: async () => {
      // Try to call logout endpoint, but logout locally regardless
      if (tokens?.access_token) {
        try {
          await authApi.logout();
        } catch {
          // Ignore errors - we'll logout locally anyway
        }
      }
    },
    onSettled: () => {
      logout();
    },
  });
};

/**
 * Hook to access authentication state.
 *
 * Returns current user, tokens, and auth status from Zustand store.
 * Automatically updates when auth state changes.
 *
 * @returns Object containing user, tokens, isAuthenticated, and isLoading
 *
 * @example
 * ```tsx
 * const { user, isAuthenticated, isLoading } = useAuthState();
 *
 * if (isLoading) return <LoadingSpinner />;
 * if (!isAuthenticated) return <Navigate to="/login" />;
 *
 * return <Dashboard user={user} />;
 * ```
 */
export const useAuthState = () => {
  const user = useAuthStore((state) => state.user);
  const tokens = useAuthStore((state) => state.tokens);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isLoading = useAuthStore((state) => state.isLoading);
  
  return {
    user,
    tokens,
    isAuthenticated,
    isLoading,
  };
};
