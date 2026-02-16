import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    // Enable source maps for debugging (can disable in production)
    sourcemap: false,
    // Increase chunk warning limit
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Vendor chunks - rarely change, cached long-term
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-query': ['@tanstack/react-query'],
          'vendor-ui': ['class-variance-authority', 'clsx', 'tailwind-merge'],
          // Feature chunks - loaded on demand
          'feature-cv': [
            './src/features/cv/pages/CVPage.tsx',
            './src/features/cv/pages/HistoryPage.tsx',
            './src/features/cv/pages/CVDetailPage.tsx',
          ],
          'feature-profile': [
            './src/features/profile/pages/ProfilesPage.tsx',
            './src/features/profile/pages/ProfileDetailPage.tsx',
            './src/features/profile/pages/ProfileEditPage.tsx',
            './src/features/profile/pages/ProfileCreatePage.tsx',
          ],
          'feature-settings': [
            './src/features/settings/pages/SettingsPage.tsx',
            './src/features/settings/pages/LlmFaqPage.tsx',
          ],
        },
      },
    },
    // Minification settings
    minify: 'esbuild',
    // Target modern browsers for smaller bundles
    target: 'es2020',
  },
})
