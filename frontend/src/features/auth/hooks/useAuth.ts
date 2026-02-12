import { useMutation } from '@tanstack/react-query';
import { useAuthStore } from '../store';
import * as authApi from '../api';
import type { LoginRequest, RegisterRequest, GoogleAuthRequest } from '../../../types';

/**
 * Hook for user registration
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
 * Hook for user login
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
 * Hook for Google OAuth
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
 * Hook for logout
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
 * Hook to get auth state
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
