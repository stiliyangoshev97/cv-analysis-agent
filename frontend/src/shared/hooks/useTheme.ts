/**
 * @fileoverview Theme Hook
 *
 * Manages dark/light mode with system preference detection
 * and localStorage persistence.
 *
 * @module shared/hooks/useTheme
 */

import { useState, useEffect, useCallback } from 'react';

type Theme = 'light' | 'dark' | 'system';

const THEME_KEY = 'cv-agent-theme';

/**
 * Get the effective theme based on system preference
 */
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
};

/**
 * Apply theme to document
 */
const applyTheme = (theme: Theme) => {
  const effectiveTheme = theme === 'system' ? getSystemTheme() : theme;
  
  if (effectiveTheme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

/**
 * useTheme Hook
 *
 * Manages application theme with persistence and system preference detection.
 *
 * @returns Theme state and controls
 *
 * @example
 * ```tsx
 * const { theme, setTheme, effectiveTheme } = useTheme();
 * 
 * <button onClick={() => setTheme('dark')}>Dark Mode</button>
 * ```
 */
export const useTheme = () => {
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(THEME_KEY) as Theme | null;
      return stored || 'system';
    }
    return 'system';
  });

  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>(() => {
    if (theme === 'system') {
      return getSystemTheme();
    }
    return theme;
  });

  // Apply theme on mount and changes
  useEffect(() => {
    applyTheme(theme);
    setEffectiveTheme(theme === 'system' ? getSystemTheme() : theme);
  }, [theme]);

  // Listen for system theme changes
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      applyTheme('system');
      setEffectiveTheme(getSystemTheme());
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(THEME_KEY, newTheme);
  }, []);

  const toggleTheme = useCallback(() => {
    const nextTheme = effectiveTheme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
  }, [effectiveTheme, setTheme]);

  return {
    /** Current theme setting ('light', 'dark', or 'system') */
    theme,
    /** Effective theme after resolving 'system' */
    effectiveTheme,
    /** Set theme */
    setTheme,
    /** Toggle between light and dark */
    toggleTheme,
    /** Whether dark mode is active */
    isDark: effectiveTheme === 'dark',
  };
};
