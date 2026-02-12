/**
 * @fileoverview Zustand auth store with localStorage persistence.
 *
 * Manages authentication state across the application:
 * - Current user data
 * - JWT tokens
 * - Authentication status
 *
 * State is persisted to localStorage and rehydrated on app load.
 *
 * @module features/auth/store/authStore
 *
 * @example
 * ```tsx
 * // In a component
 * const user = useAuthStore((state) => state.user);
 * const logout = useAuthStore((state) => state.logout);
 *
 * // Or use the useAuthState hook for common patterns
 * const { user, isAuthenticated } = useAuthState();
 * ```
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User, TokenResponse } from '../../../types';

/**
 * Auth store state interface.
 *
 * @interface AuthState
 */
interface AuthState {
  // ========================
  // State
  // ========================

  /** Currently authenticated user, null if not logged in */
  user: User | null;

  /** JWT tokens for API authentication */
  tokens: TokenResponse | null;

  /** Whether user is authenticated */
  isAuthenticated: boolean;

  /** Loading state during initial rehydration */
  isLoading: boolean;
  
  // ========================
  // Actions
  // ========================

  /**
   * Set authenticated user and tokens.
   * Called after successful login or registration.
   *
   * @param user - User data from API
   * @param tokens - JWT tokens from API
   */
  setAuth: (user: User, tokens: TokenResponse) => void;

  /**
   * Update tokens without changing user.
   * Called after token refresh.
   *
   * @param tokens - New JWT tokens
   */
  setTokens: (tokens: TokenResponse) => void;

  /**
   * Set loading state.
   *
   * @param isLoading - New loading state
   */
  setLoading: (isLoading: boolean) => void;

  /**
   * Clear all auth state.
   * Called on logout or session expiry.
   */
  logout: () => void;
}

/** LocalStorage key for persisted auth state */
const STORAGE_KEY = 'cv-agent-auth';

/**
 * Zustand auth store with persistence.
 *
 * Uses localStorage to persist user and tokens across sessions.
 * Automatically rehydrates on app load.
 *
 * @example
 * ```tsx
 * // Get state
 * const user = useAuthStore((state) => state.user);
 *
 * // Call action
 * const setAuth = useAuthStore((state) => state.setAuth);
 * setAuth(user, tokens);
 *
 * // Or use selector pattern
 * const { user, logout } = useAuthStore();
 * ```
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // ========================
      // Initial State
      // ========================
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: true, // Start as loading to check stored auth
      
      // ========================
      // Actions
      // ========================
      setAuth: (user, tokens) => set({
        user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
      }),
      
      setTokens: (tokens) => set({ tokens }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      logout: () => set({
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
      }),
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => localStorage),
      /**
       * Only persist these fields to localStorage.
       * Excludes isLoading as it's a transient state.
       */
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
      /**
       * Called after rehydration from localStorage.
       * Sets loading to false once state is restored.
       */
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.setLoading(false);
        }
      },
    }
  )
);
