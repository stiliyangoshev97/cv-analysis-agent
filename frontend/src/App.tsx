/**
 * @fileoverview Main application component.
 *
 * Sets up the app with React Router for navigation.
 *
 * @module App
 */

import { RouterProvider } from 'react-router-dom';
import { router } from '@/router';

/**
 * Main application component.
 *
 * Uses React Router for client-side navigation between pages.
 *
 * @returns The main app component with router
 */
const App = () => {
  return <RouterProvider router={router} />;
};

export default App;
