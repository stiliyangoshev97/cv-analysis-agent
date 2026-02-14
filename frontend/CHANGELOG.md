# Changelog

All notable changes to the CV Analysis Agent frontend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.10.0] - 2026-02-14 📦 BATCH CV UPLOAD

### Added

**Batch Upload System**
- `CVFileList` component - Displays staged CVs with status indicators
  - Shows file name, size, and upload status
  - Progress bar during scanning
  - Success/error icons and messages
  - Remove button for pending files

**New Upload Flow**
- Users can now add up to 10 CVs before scanning
- Files are staged first for review
- "Scan CVs" button to confirm and start evaluation
- Duplicate file detection (by filename)
- "Clear All" and "Upload More CVs" buttons

### Changed

**FileDropzone**
- Added `multiple` prop for batch mode
- Added `onFilesSelect` callback for multiple files
- Added `maxFiles` prop (default: 10)
- Updated UI to show batch mode text
- Added dark mode support

**CVPage**
- Complete rewrite for batch upload workflow
- Stage files → Review → Confirm → Scan
- Sequential upload processing with progress
- Multiple results displayed in a list
- "Clear All Results" option

---

## [0.9.0] - 2026-02-14 🌙 DARK MODE & THEME SUPPORT

### Added

**Theme System**
- `useTheme` hook - Theme state management with localStorage persistence
  - Supports 'light', 'dark', and 'system' modes
  - Automatic system preference detection via `prefers-color-scheme`
  - Applies 'dark' class to document root for Tailwind dark mode
- `ThemeToggle` component - Toggle button with sun/moon icons
  - Animated icon transitions
  - Keyboard accessible

**Dark Mode Styling**
- Updated `tailwind.config.js` with `darkMode: 'class'` strategy
- Added custom dark color tokens in Tailwind config
- Updated `index.css` with dark mode CSS variables

### Changed

**Core UI Components - Dark Mode Variants**
- `RootLayout` - Dark backgrounds, borders, and ThemeToggle in header
- `Card` - Dark backgrounds and borders for all variants
- `CardTitle` / `CardDescription` / `CardFooter` - Dark text colors
- `Button` - Dark variants for all button styles (primary, secondary, outline, ghost, danger)
- `Input` - Dark backgrounds, borders, labels, and error states
- `Select` - Dark backgrounds, borders, and dropdown arrow
- `Textarea` - Dark backgrounds, borders, and helper text
- `Text` - Dark text colors for all variants (default, muted, error, success)
- `Heading` - Dark text color
- `Badge` - Dark backgrounds with adjusted opacity for colored variants
- `ProgressBar` - Dark track and fill colors
- `ErrorBoundary` - Dark backgrounds and icon colors

---

## [0.8.0] - 2026-02-14 ✨ POLISH (Error Handling & Toasts)

### Added

**CV List Infrastructure**
- `cvSummarySchema` / `cvListResponseSchema` - Schemas for CV list endpoint
- `listCVs()` API function - Fetch paginated list of user's CVs
- `useCVList()` hook - React Query hook for CV list
- `cvKeys` - Query key factory for CV caching

**Compare CVs Modal (`features/chat/components/CompareCVsModal.tsx`)**
- Select 2-5 CVs to compare with checkboxes
- Optional comparison focus question input
- AI-powered comparison analysis display
- Candidate ranking with visual ranking badges
- Score and status badges for each CV

### Changed
- `CVPage` - Added "Compare CVs" button in page header
  - Opens CompareCVsModal for candidate comparison
  - Added page title and description header

---

## [0.8.0] - 2026-02-14 ✨ POLISH (Error Handling & Toasts)

### Added

**Toast Notifications (`shared/components/ui/Toast.tsx`)**
- Integrated Sonner for toast notifications
- ToastProvider component for app-level setup
- toast utility with typed methods:
  - `toast.success(message, description?)` - Success notifications
  - `toast.error(message, description?)` - Error notifications
  - `toast.info(message, description?)` - Info notifications
  - `toast.warning(message, description?)` - Warning notifications
  - `toast.loading(message)` - Loading state toasts
  - `toast.promise(promise, options)` - Promise-based toasts
- Rich colors and close buttons
- Custom styling with Tailwind classes

**Error Boundaries (`shared/components/ui/ErrorBoundary.tsx`)**
- `ErrorBoundary` - Catches React errors and shows fallback UI
- `PageErrorBoundary` - Full-page error boundary with navigation
- Development mode shows error details
- Try Again and Reload Page buttons

**Global Error Handling**
- Enhanced API client error interceptor
- Extracts user-friendly error messages from responses
- Handles 401 (auto-logout), 429 (rate limit), 500+ (server errors)

### Changed
- `main.tsx` - Wrapped app with PageErrorBoundary and ToastProvider
- `useSettings` hooks - Added toast notifications for API key and config operations
- `useChat` hooks - Added toast notifications for errors
- `useUploadCV` hook - Added toast on successful evaluation
- API client - Enhanced error message extraction

---

## [0.7.0] - 2026-02-14 🔄 COMPARE CVs MODAL

### Added

**CV List API & Hooks**
- `cvSummarySchema` / `cvListResponseSchema` - Zod schemas for CV lists
- `listCVs()` - API function to fetch user's CVs
- `useCVList()` - React Query hook with caching

**CompareCVsModal Component**
- Select 2-5 CVs from list with checkbox interface
- Optional comparison focus question input
- AI-powered comparison analysis display
- Candidate ranking with visual badges (1st, 2nd, 3rd...)
- Score and status badges per candidate
- Reset to compare different CVs

### Changed
- `CVPage` - Added "Compare CVs" button in page header
- Updated schema and type exports

---

## [0.6.0] - 2026-02-14 💬 CHAT UI (Ask AI & Explain Criteria)

### Added

**Chat Feature Module (`features/chat/`)**
- Complete RAG-powered chat functionality for CV analysis
- "Ask AI" button on scorecards to start conversations
- "Why?" buttons on criteria for detailed explanations

**Zod Schemas (`shared/schemas/chat.schemas.ts`)**
- `chatMessageSchema` - Individual chat messages (user/assistant roles)
- `chatHistoryResponseSchema` - Chat history with pagination
- `askQuestionRequestSchema` / `askQuestionResponseSchema` - Ask questions
- `explainCriterionResponseSchema` - Criterion explanations with evidence
- `compareCvsRequestSchema` / `compareCvsResponseSchema` - CV comparison

**API Functions (`features/chat/api/chatApi.ts`)**
- `askQuestion(cvId, message)` - Ask a question about a CV
- `getChatHistory(cvId, limit)` - Get chat history
- `clearChatHistory(cvId)` - Clear chat history
- `explainCriterion(cvId, criterion, includeEvidence)` - Explain a score
- `compareCVs(cvIds, question)` - Compare multiple CVs

**React Query Hooks (`features/chat/hooks/useChat.ts`)**
- `useChatHistory(cvId, limit)` - Fetch chat history
- `useAskQuestion()` - Mutation for asking questions
- `useClearChatHistory()` - Mutation for clearing history
- `useExplainCriterion()` - Mutation for explaining criteria
- `useCompareCVs()` - Mutation for comparing CVs

**Components**
- `ChatMessage` - Individual chat message bubble (user/assistant styling)
- `ChatPanel` - Slide-out panel for full chat interface
  - Message history with auto-scroll
  - Input field with Enter to send
  - Clear history button
  - Empty state with example questions
- `ExplainModal` - Modal for criterion explanations
  - Shows score with visual progress bar
  - Detailed explanation text
  - Evidence excerpts from CV

### Changed
- `CriteriaItem` - Added "Why?" button to trigger ExplainModal
- `Scorecard` - Added "Ask AI" button to open ChatPanel
  - Passes cvId to CriteriaItem for explain functionality

---

## [0.5.0] - 2026-02-14 ⚙️ SETTINGS PAGE (API Keys & LLM Preferences)

### Added

**Settings Feature Module (`features/settings/`)**
- Complete settings management for API keys and LLM preferences
- Required for CV uploads to work (OpenAI key mandatory for embeddings)

**Zod Schemas (`shared/schemas/settings.schemas.ts`)**
- `aiProviderSchema` - AI provider types (openai, anthropic, gemini)
- `llmProviderSchema` - LLM provider types
- `apiKeyInfoSchema` - API key info (hints only)
- `apiKeyListResponseSchema` - List of configured keys
- `setApiKeyRequestSchema` / `setApiKeyResponseSchema` - Set key request/response
- `validateKeyRequestSchema` / `validateKeyResponseSchema` - Validate key
- `agentConfigResponseSchema` - Agent configuration
- `updateAgentConfigRequestSchema` - Update agent config
- `availableModelsResponseSchema` - Available LLM models
- `setupStatusResponseSchema` - Setup completion status

**API Functions (`features/settings/api/settingsApi.ts`)**
- `getApiKeys()` - List configured API keys
- `setApiKey(provider, apiKey)` - Set/update an API key
- `deleteApiKey(provider)` - Delete an API key
- `validateApiKey(provider, apiKey)` - Validate key without storing
- `getAgentConfig()` - Get LLM preferences
- `updateAgentConfig(data)` - Update LLM preferences
- `getAvailableModels()` - List available models
- `getSetupStatus()` - Check if setup is complete

**React Query Hooks (`features/settings/hooks/useSettings.ts`)**
- `useApiKeys()` - Fetch API keys
- `useSetApiKey()` - Mutation for setting keys
- `useDeleteApiKey()` - Mutation for deleting keys
- `useValidateApiKey()` - Mutation for validating keys
- `useAgentConfig()` - Fetch agent configuration
- `useUpdateAgentConfig()` - Mutation for updating config
- `useAvailableModels()` - Fetch available models
- `useSetupStatus()` - Check setup status

**Components**
- `ApiKeysTab` - Manage API keys for OpenAI, Anthropic, and Gemini
  - Add/update/delete keys per provider
  - Validate keys before saving (test API calls)
  - Shows key hints (last 4 chars)
  - Warning when OpenAI not configured
- `LlmPreferencesTab` - Configure LLM preferences
  - Select default LLM provider and model
  - Per-agent overrides (Chat Agent, Scorer Agent)
  - Shows effective provider for each agent
  - Embeddings always use OpenAI (read-only)
- `SettingsPage` - Two-tab interface for settings
- `SetupBanner` - Persistent warning banner shown when setup incomplete
  - Appears at top of all pages
  - Links to settings page
  - Auto-hides when setup is complete
- `SetupRequiredScreen` - Full-page blocker for CV upload
  - Shows what's missing
  - Explains why API keys are needed
  - Links to settings page

**Routes**
- Added `/settings` route for API Keys & LLM Preferences page

**UserMenu Enhancement**
- Added "Settings" link with gear icon
- Now shows both Settings and Notification Settings

**CV Upload Blocking**
- CVPage now checks setup status before allowing uploads
- Shows SetupRequiredScreen if OpenAI key not configured

### Changed

**RootLayout**
- Added SetupBanner component to show persistent warning

**Routes Configuration**
- Added `/settings` route before `/settings/notifications`
- Updated route documentation

### Architecture

```
Settings Flow:
┌─────────────────┐    ┌────────────────┐    ┌─────────────────┐
│ Settings Page   │───▶│ /api/settings  │───▶│ Encrypted DB    │
│ (2 Tabs)        │    │ Endpoints      │    │ Storage         │
└─────────────────┘    └────────────────┘    └─────────────────┘
        │
   ┌────┴─────┐
   ▼          ▼
API Keys    LLM Preferences
Tab         Tab
```

---

## [0.4.0] - 2026-02-13 🔔 NOTIFICATION SETTINGS UI (Phase 5)

### Added

**React Router Integration**
- Added proper React Router (v7) configuration
- Created `routes.tsx` with route definitions
- Header logo now links to home page
- Catch-all route redirects to home

**Notification Feature Module (`features/notification/`)**
- `notificationApi.ts` - API functions for notification endpoints
- `useNotificationSettings.ts` - React Query hooks:
  - `useNotificationSettings()` - Fetch settings
  - `useUpdateNotificationSettings()` - Update settings mutation
  - `useSendTestNotification()` - Send test notification mutation
  - `useNotificationStatus()` - Fetch service status
- `NotificationSettingsPanel.tsx` - Main settings UI component
- `NotificationSettingsPage.tsx` - Page wrapper
- `Toggle.tsx` - Custom toggle switch component
- `ThresholdSlider.tsx` - Score threshold slider component

**Notification Schemas (`shared/schemas/notification.schemas.ts`)**
- `notificationSettingsSchema` - Settings validation
- `notificationSettingsUpdateSchema` - Update request validation
- `notificationChannelSchema` - Channel enum (email/whatsapp)
- `notificationResultSchema` - Test result validation
- `notificationServiceStatusSchema` - Service status validation

**User Menu Enhancement**
- Added "Notification Settings" link to user dropdown
- Bell icon for visual clarity
- Links to `/settings/notifications`

### Changed

**App.tsx**
- Converted to use `RouterProvider` from React Router
- Routes now defined in `router/routes.tsx`

**RootLayout**
- Logo/header now wrapped in `Link` to home page
- Imported `Link` from `react-router-dom`

**Router Index**
- Added `router` export from `routes.tsx`
- Updated module documentation

### Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | `CVPage` | CV Upload & Evaluation (protected) |
| `/settings/notifications` | `NotificationSettingsPage` | Notification preferences (protected) |

---

## [0.3.0] - 2026-02-12 🏗️ REFACTORING + UI COMPONENTS

### Added

**Shared UI Component Library (CVA-based)**
- `Button` - 5 variants (primary, secondary, outline, ghost, danger), 3 sizes, loading state
- `Badge` - 5 variants (default, success, warning, error, info), 3 sizes
- `Card` - 3 variants, sub-components (CardHeader, CardTitle, CardDescription, CardContent, CardFooter)
- `Input` - forwardRef, label, error, helperText support
- `Textarea` - forwardRef, label, error support
- `Select` - forwardRef, custom arrow, options array
- `Text` - 4 sizes, 4 colors, 3 weights, polymorphic `as` prop
- `Heading` - levels 1-6, auto semantic h1-h6 element
- `Spinner` - 4 sizes, accessible
- `Container` - 4 size variants (sm, md, lg, full)
- `ProgressBar` - with accessibility attributes

**Path Aliases**
- Added `@/` alias to `tsconfig.app.json` and `vite.config.ts`
- Clean imports: `import { Button } from '@/shared/components/ui'`

**Documentation**
- Comprehensive JSDoc comments for all components
- Updated README.md with component examples
- Updated PROJECT_CONTEXT.md with architecture

### Changed

**Project Structure Refactoring**
- Merged `cv-upload/` + `scorecard/` → unified `cv/` feature
- Moved `lib/api.ts` → `shared/api/apiClient.ts`
- Moved `components/ui/` → `shared/components/ui/`
- Moved `schemas/` → `shared/schemas/`
- Moved `types/` → `shared/types/`
- Created `providers/` directory for QueryProvider
- Created `router/` directory with RootLayout and guards

**Components Refactored to Use Shared UI**
- `RootLayout` → uses Container, Text, Heading
- `CVPage` → uses Heading, Text
- `Scorecard` → uses Card, CardContent, CardFooter, Text, Heading, Badge, Button
- `CriteriaItem` → uses Badge, Text
- `UploadProgress` → uses Card, ProgressBar, Spinner, Text
- `LoginForm` / `RegisterForm` → uses Button
- `FileDropzone` → uses `cn()` utility

**Dependencies**
- Added `class-variance-authority` for variant-based styling
- Added `tailwind-merge` for class merging
- Added `clsx` for conditional classes

### Removed
- Old `lib/` directory
- Old `components/` directory at root
- Old `schemas/` and `types/` at root
- `features/cv-upload/` and `features/scorecard/` (merged)

---

## [0.2.0] - 2025-02-12 🔐 AUTHENTICATION UI

### Added

**Auth Store (Zustand)**
- `useAuthStore` - Persistent auth state management
- Stores user, tokens, authentication status
- Persists to localStorage for session persistence
- Auto-rehydration on app load

**Auth API Integration**
- `register()` - Register new user
- `login()` - Login with email/password
- `refreshToken()` - Refresh access token
- `googleAuth()` - Google OAuth exchange
- `getMe()` - Get current user
- `logout()` - Server logout acknowledgement

**Auth Hooks**
- `useRegister()` - Registration mutation
- `useLogin()` - Login mutation
- `useLogout()` - Logout mutation
- `useGoogleAuth()` - Google OAuth mutation
- `useAuthState()` - Get auth state

**Auth Components**
- `LoginForm` - Email/password login form
- `RegisterForm` - User registration form with validation
- `AuthPage` - Combined auth page with form switching
- `UserMenu` - Dropdown menu with user info and logout
- `ProtectedRoute` - Route wrapper requiring authentication

**API Client Updates**
- Added auth token interceptor (auto-attach Bearer token)
- Added 401 response handler (auto-logout on expired token)

### Changed
- Wrapped main app in `ProtectedRoute`
- Added `UserMenu` to header for authenticated users

### Dependencies
- Added `zustand` for state management
- Added `react-router-dom` for routing
- Added `@react-oauth/google` for Google OAuth

---

## [0.1.0] - 2025-01-XX 🚀 MVP RELEASE

### Added

**File Upload Feature**
- `FileDropzone` component with drag-and-drop support
- Single file upload enforcement (explicit error for multiple files)
- PDF file type validation
- Visual feedback during drag hover state
- File icon display with selected filename

**Upload Progress**
- `UploadProgress` component showing real-time upload progress
- `useUploadCV` hook with TanStack Query mutation
- Axios-based upload with progress tracking

**Scorecard Display**
- `Scorecard` component for evaluation results
- `ScoreRing` circular score visualization with dynamic colors
- `CriteriaItem` component for individual criterion display
- Pass/Fail badge with appropriate coloring
- Score breakdown with met/unmet indicators

**Reusable UI Components**
- `Button` with CVA variants (primary, secondary, outline, ghost, danger)
- `Badge` with status variants (success, error, warning, info, neutral)
- `ProgressBar` for linear progress indication

**API Integration**
- Axios client with base URL configuration
- `uploadCV` function with progress callback support
- TypeScript interfaces matching backend schemas

**Project Configuration**
- Vite + React + TypeScript setup
- TailwindCSS with custom configuration
- TanStack Query for server state management
- Feature-based folder structure

### Changed

**Single CV Evaluation**
- Simplified from batch processing to single CV evaluation
- New upload replaces previous result (no accumulation)

### Fixed

**Multi-File Prevention**
- Added explicit error message when user attempts to upload multiple files
- Clear feedback: "Please upload only one PDF file at a time"

---

## [Unreleased]

### Planned - Phase 1: Authentication UI
- Login page with email/password
- Registration page
- Google OAuth button
- Auth context/store with Zustand
- Protected route wrapper
- JWT token management

### Planned - Phase 7: Frontend Enhancements
- Dashboard with CV history
- Candidate comparison view (Match-Up feature)
- Semantic search interface
- Notification preferences UI
- Chat interface for CV Q&A
- Batch upload with queue management
