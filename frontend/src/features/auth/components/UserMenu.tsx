/**
 * @fileoverview UserMenu Component
 *
 * Dropdown menu displaying user info and logout action.
 * Shows in the app header when user is authenticated.
 *
 * @module features/auth/components/UserMenu
 *
 * FEATURES:
 * - User avatar or initials display
 * - Dropdown menu on click
 * - User name and email display
 * - Logout action with loading state
 * - Click outside to close
 *
 * @example
 * ```tsx
 * // In header component
 * <UserMenu />
 * ```
 */

import { useState, useRef, useEffect } from 'react';
import { useLogout, useAuthState } from '../hooks';

/**
 * UserMenu Component
 *
 * Dropdown menu for authenticated user actions.
 *
 * @returns User menu element or null if not authenticated
 */
export const UserMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user } = useAuthState();
  const { mutate: logout, isPending: isLoggingOut } = useLogout();
  
  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  if (!user) return null;
  
  const initials = user.full_name
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
  
  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-1 rounded-lg hover:bg-gray-100 transition-colors"
      >
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.full_name}
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-white">{initials}</span>
          </div>
        )}
        <span className="text-sm font-medium text-gray-700 hidden sm:block">
          {user.full_name}
        </span>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          <div className="px-4 py-3 border-b border-gray-100">
            <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
            <p className="text-sm text-gray-500 truncate">{user.email}</p>
          </div>
          
          <div className="py-1">
            <button
              onClick={() => {
                setIsOpen(false);
                logout();
              }}
              disabled={isLoggingOut}
              className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              {isLoggingOut ? 'Signing out...' : 'Sign out'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
