/**
 * @fileoverview RegisterForm Component
 *
 * User registration form with email, password, and name fields.
 * Includes client-side validation and error handling.
 *
 * @module features/auth/components/RegisterForm
 *
 * FEATURES:
 * - Full name, email, password fields
 * - Password confirmation validation
 * - Password strength validation (min 8 chars)
 * - Loading state during submission
 * - API error display
 * - Switch to login link
 *
 * @example
 * ```tsx
 * <RegisterForm onSwitchToLogin={() => setView('login')} />
 * ```
 */

import { useState } from 'react';
import { useRegister } from '../hooks';
import { Button } from '@/shared/components/ui';

/**
 * RegisterForm component props.
 */
interface RegisterFormProps {
  /** Callback to switch to login view */
  onSwitchToLogin: () => void;
}

/**
 * RegisterForm Component
 *
 * Renders a registration form with validation.
 *
 * @param props - Component props
 * @returns Registration form element
 */
export const RegisterForm = ({ onSwitchToLogin }: RegisterFormProps) => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const { mutate: register, isPending, error } = useRegister();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    
    // Validate password match
    if (password !== confirmPassword) {
      setValidationError('Passwords do not match');
      return;
    }
    
    // Validate password length
    if (password.length < 8) {
      setValidationError('Password must be at least 8 characters');
      return;
    }
    
    register({ email, password, full_name: fullName });
  };
  
  // Extract error message from axios error or regular error
  const getErrorMessage = () => {
    if (!error) return null;
    const axiosError = error as { response?: { data?: { detail?: string } } };
    return axiosError.response?.data?.detail || error.message;
  };
  const apiError = getErrorMessage();
  const displayError = validationError || apiError;
  
  return (
    <div className="w-full max-w-md">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white text-center mb-2">
          Create Account
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-center mb-6">
          Join CV Analysis Agent to start screening candidates
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {displayError && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <p className="text-sm text-red-600 dark:text-red-400">{displayError}</p>
            </div>
          )}
          
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Full Name
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Smith"
              required
              minLength={2}
              maxLength={100}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:border-blue-400 outline-none transition-colors"
            />
          </div>
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:border-blue-400 outline-none transition-colors"
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={8}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:border-blue-400 outline-none transition-colors"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Must be at least 8 characters</p>
          </div>
          
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:border-blue-400 outline-none transition-colors"
            />
          </div>
          
          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            disabled={isPending}
          >
            {isPending ? 'Creating account...' : 'Create Account'}
          </Button>
        </form>
        
        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Already have an account?{' '}
          <button
            type="button"
            onClick={onSwitchToLogin}
            className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
};
