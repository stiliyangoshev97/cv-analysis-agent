/**
 * @fileoverview Main application component.
 *
 * Sets up the app with protected routes and layouts.
 *
 * @module App
 */

import { RootLayout, ProtectedRoute } from '@/router';
import { CVPage } from '@/features/cv';

/**
 * Main application component.
 *
 * Wraps the CV page in protected route and root layout.
 *
 * @returns The main app component
 */
const App = () => {
  return (
    <ProtectedRoute>
      <RootLayout>
        <CVPage />
      </RootLayout>
    </ProtectedRoute>
  );
};

export default App;
