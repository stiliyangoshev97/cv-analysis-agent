import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User, TokenResponse } from '../../../types';

interface AuthState {
  // State
  user: User | null;
  tokens: TokenResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setAuth: (user: User, tokens: TokenResponse) => void;
  setTokens: (tokens: TokenResponse) => void;
  setLoading: (isLoading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: true, // Start as loading to check stored auth
      
      // Actions
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
      name: 'cv-agent-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // After rehydration, set loading to false
        if (state) {
          state.setLoading(false);
        }
      },
    }
  )
);
