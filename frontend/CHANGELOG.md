# Changelog

All notable changes to the CV Analysis Agent frontend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.18.0] - 2026-02-17 📜 Notification History

### Added

**Notification History Page** (`/settings/notifications/history`)
- View all sent notifications with paginated list
- Filter by type (Email/WhatsApp) and status (Sent/Failed/Pending)
- Statistics cards showing total, sent, failed, and pending counts
- Resend failed notifications with one click
- Delete notification entries
- Relative time display (e.g., "5m ago", "2d ago")
- Status badges with color coding

**New Files**
- `NotificationHistoryPage.tsx` - Full history page component
- `useNotificationHistory.ts` - React Query hooks for history API
- History-related Zod schemas in `notification.schemas.ts`
- API functions in `notificationApi.ts`

**UI Improvements**
- "View History" button added to Notification Settings page
- Link from history back to settings

---

## [0.17.0] - 2026-02-16 🚀 Performance & SEO Optimization

### Added

**Lazy Loading & Code Splitting**
- All page components now use `React.lazy()` for dynamic imports
- Created `withSuspense()` helper for consistent loading states
- New `PageLoader` component for Suspense fallback
- Each route loads its chunk on-demand, reducing initial bundle size

**Vite Build Optimization**
- Manual chunk splitting for vendor libraries:
  - `vendor-react`: React, React-DOM, React Router (~89KB)
  - `vendor-query`: TanStack Query (~48KB)
  - `vendor-ui`: CVA, clsx, tailwind-merge (~26KB)
- Feature-based code splitting (cv, profile, settings)
- ES2020 target for smaller bundles
- esbuild minification

**SEO Improvements**
- Complete favicon support: SVG, ICO, PNG (96x96), Apple Touch Icon
- Web App Manifest with PWA support
- Open Graph meta tags for social sharing
- Twitter Card meta tags
- Theme color for mobile browsers
- Dark mode flash prevention script
- Initial loading spinner before React hydrates

**Query Cache Invalidation Fix**
- CV list cache now invalidates after successful upload
- History page updates immediately without manual refresh

### Changed

**Files Modified**
- `routes.tsx` - Converted to lazy imports with Suspense
- `vite.config.ts` - Added build optimization config
- `index.html` - Full SEO and favicon setup
- `site.webmanifest` - PWA manifest with app metadata
- `useUploadCV.ts` - Added cache invalidation on success

**New Files**
- `PageLoader.tsx` - Loading spinner for route transitions
- Favicon files: `favicon.svg`, `favicon.ico`, `favicon-96x96.png`, `apple-touch-icon.png`, `logo.svg`
- `web-app-manifest-192x192.png`, `web-app-manifest-512x512.png`

---

## [0.16.1] - 2026-02-16 🌙 Dark Mode Fixes

### Fixed

**UserMenu Dark Mode**
- Fixed username visibility in dark mode by adding `dark:text-gray-300`

---

## [0.16.0] - 2026-02-16 🤖 Parser Agent Configuration

### Added

**Parser Agent configuration in LLM Preferences**
- New "Parser Agent" section in Per-Agent Overrides
- Configure which LLM provider/model to use for document extraction
- Default is Gemini (fast & cost-effective)
- Shows "Document Processing" badge
- Displays effective provider that will be used

**Schema Updates**
- Added `parser_provider` and `parser_model` to `AgentConfigResponse` schema
- Added `parser_provider` and `parser_model` to `UpdateAgentConfigRequest` schema

---

## [0.15.0] - 2026-02-16 🔄 RE-EVALUATE FEATURE

### Added

**Re-evaluate CV with Different Profile**
- "Re-evaluate" button on CV detail page header
- `ReEvaluateModal` component with profile selector
- Shows all available profiles (system + user-created)
- Current profile marked with "Current" badge
- System templates marked with "System" badge
- Warning message about replacing previous evaluation
- Loading state during re-evaluation
- Auto-refresh of CV data after successful re-evaluation

**New Files**
- `ReEvaluateModal.tsx` - Modal component for profile selection
- `useReEvaluateCV.ts` - React Query mutation hook

**API**
- `reEvaluateCV(cvId, templateId)` - API function for re-evaluation

---

## [0.14.0] - 2026-02-16 🔑 BYOK NOTIFICATIONS (Bring Your Own Keys)

### Added

**SMTP Configuration UI**
- Collapsible SMTP configuration section in Email Notifications card
- Form fields: Host, Port, Username, Password, From Email, From Name, Use TLS
- Shows current configuration status with masked credentials
- "Clear" button to remove custom SMTP configuration
- Confirmation dialog before clearing

**Twilio Configuration UI**
- Collapsible Twilio configuration section in WhatsApp Notifications card
- Form fields: Account SID, Auth Token, WhatsApp From Number
- Shows current configuration status with masked credentials
- "Clear" button to remove custom Twilio configuration
- Confirmation dialog before clearing

**Configuration Source Indicators**
- Badge shows "BYOK" (green) when using user credentials
- Badge shows "Not Configured" (gray) when not set up
- No server fallback - pure BYOK architecture

**New Schemas (`notification.schemas.ts`)**
- `SmtpConfigUpdate` - SMTP configuration update request
- `SmtpConfigResponse` - SMTP configuration response with masked credentials
- `TwilioConfigUpdate` - Twilio configuration update request
- `TwilioConfigResponse` - Twilio configuration response with masked credentials
- Updated `NotificationSettings` to include SMTP/Twilio config
- Updated `NotificationSettingsUpdate` to accept SMTP/Twilio config
- Updated `NotificationServiceStatus` with `email_source` and `whatsapp_source`

**New API Functions (`notificationApi.ts`)**
- `clearSmtpConfig()` - Clear user's SMTP configuration
- `clearTwilioConfig()` - Clear user's Twilio configuration

**New Hooks (`useNotificationSettings.ts`)**
- `useClearSmtpConfig()` - Mutation for clearing SMTP config
- `useClearTwilioConfig()` - Mutation for clearing Twilio config

### Changed

**NotificationSettingsPanel**
- Complete redesign to support BYOK configuration
- Added collapsible SMTP and Twilio configuration sections
- Added SettingsIcon, ChevronDownIcon, ChevronUpIcon components
- Save button now enabled when SMTP/Twilio config is provided
- Form fields clear after save (credentials stored encrypted on server)
- Confirmation dialogs for clearing configurations

---

## [0.13.0] - 2026-02-16 🔍 CV SIMILARITY & SEARCH

### Added

**Find Similar CVs Feature**
- "Find Similar" button on CV detail page header
- `SimilarCVsModal` component showing similar candidates with similarity scores
- Links to similar CV detail pages from modal

**CV Ranking/Percentile Display**
- `RankingBadge` component showing percentile ranking (e.g., "Top 10%")
- `RankingInline` component for compact ranking display in lists
- Ranking badge shown on CV detail page next to score
- Inline ranking shown on CV history cards

**Semantic Search**
- `SemanticSearchBar` component for natural language CV search
- AI-powered search on history page (e.g., "Python developer with fintech experience")
- `SearchResults` component displaying search results with relevance scores
- Clear search functionality

**CV Comparison**
- "Compare CVs" button on history page header
- `CVComparisonModal` for comparing 2-10 CVs side-by-side
- CV selection interface with checkboxes
- Similarity matrix visualization
- Best match highlighting
- Most similar pair identification

**New Schemas**
- `similarCVSchema` - Similar CV response
- `similarCVsResponseSchema` - Similar CVs endpoint response
- `cvRankingResponseSchema` - CV ranking/percentile response
- `cvComparisonItemSchema` - CV in comparison
- `cvCompareRequestSchema` / `cvCompareResponseSchema` - Comparison request/response
- `cvSearchRequestSchema` / `cvSearchResponseSchema` - Semantic search request/response

**New API Functions**
- `findSimilarCVs(cvId, limit, minSimilarity)` - Find similar CVs
- `getCVRanking(cvId)` - Get CV percentile ranking
- `compareCVs(cvIds)` - Compare multiple CVs
- `searchCVs(query, limit, minSimilarity)` - Semantic search

**New React Query Hooks**
- `useSimilarCVs(cvId, limit, minSimilarity, enabled)` - Find similar CVs
- `useCVRanking(cvId, enabled)` - Get ranking
- `useCompareCVs()` - Mutation for comparison
- `useSearchCVs(query, limit, minSimilarity, enabled)` - Reactive search
- `useSearchCVsMutation()` - On-demand search mutation

### Fixed

**Similar CVs Accuracy**
- Increased default minimum similarity threshold from 0 to 0.3 (30%)
- `SimilarCVsModal` uses 0.5 (50%) for stricter filtering
- Dissimilar CVs no longer appear in "Find Similar" results

### Changed

**CV Detail Page (`CVDetailPage.tsx`)**
- Added "Find Similar" button next to "Ask AI" button
- Added `RankingBadge` component showing percentile next to score
- Added `SimilarCVsModal` for displaying similar candidates

**History Page (`HistoryPage.tsx`)**
- Added "Compare CVs" button in header (when 2+ CVs exist)
- Added AI-Powered Search section with `SemanticSearchBar`
- Added `SearchResults` display when search is active
- Added `RankingInline` to CV history cards
- Added `CVComparisonModal` for comparing selected CVs

---

## [0.12.2] - 2026-02-15 💬 CV DETAIL CHAT & ID FIX

### Added

**Chat Panel on CV Detail Page**
- "Ask AI" button on CV detail page header
- Opens ChatPanel for RAG-powered Q&A about the CV
- Uses correct CV ID from database for chat API calls

### Fixed

**CV ID in Upload Response**
- Updated `uploadResponseSchema` to include `cv_id` field
- `CVPage` now uses actual CV ID from backend instead of `crypto.randomUUID()`
- Chat functionality now works correctly after CV upload

### Changed

**CV Page (`CVPage.tsx`)**
- Changed from `id: crypto.randomUUID()` to `id: data.cv_id`
- Chat now uses the real database CV ID

**CV Detail Page (`CVDetailPage.tsx`)**
- Added `ChatPanel` component import
- Added `showChat` state for panel visibility
- Added "Ask AI" button next to Delete button

---

## [0.12.1] - 2026-02-15 📝 IMPROVED PROFILE CREATION UX

### Added

**Helpful Placeholder Examples in Profile Creation**
- Profile name placeholder: `"e.g., Senior Backend Developer, AI/ML Engineer, Product Manager"`
- Profile description placeholder: Full example describing ideal candidate
- Criterion name placeholder: `"e.g., Python Experience, Cloud Infrastructure, Leadership Skills"`
- Criterion description placeholder: Detailed example of skill evaluation
- Keywords placeholder: `"e.g., python, django, fastapi, flask"` with usage hints
- Evaluation guidelines placeholder: Comprehensive scoring rubric example

**Helper Text for All Form Fields**
- Added explanatory text below each input field
- Clear guidance on what information to provide
- Instructions for keyword input (press Enter to add)

### Fixed

**Profile Creation Sort Order Bug**
- Fixed `sort_order: -1` validation error when creating profiles
- `criteria.indexOf()` was always returning -1 due to object reference comparison
- Now correctly uses array index for sort order

---

## [0.12.0] - 2026-02-15 📜 CV EVALUATION HISTORY

### Added

**CV Evaluation History Page (`HistoryPage.tsx`)**
- New page to view all CV evaluations with filtering and sorting
- Search by candidate name or filename
- Filter by evaluation status (All/Passed/Failed)
- Sort by date or score
- Statistics overview (total CVs, avg score, pass rate)
- Responsive card-based layout for CV items
- Score and status badges with color coding
- Relative time display (Today, Yesterday, X days ago)
- Empty state with CTA to upload first CV
- Link to individual CV details

**CV Detail Page (`CVDetailPage.tsx`)**
- Full CV detail view with evaluation results
- Shows candidate name, filename, upload date
- Score and status badges
- AI analysis/reasoning section
- Per-criterion scores with progress bars and evidence
- Delete CV functionality with confirmation modal
- Route: `/history/:id`

**CV Delete Functionality**
- Delete button on each CV in history list
- Confirmation modal before deletion
- `deleteCV` API function to call `DELETE /api/cv/{id}`
- `useDeleteCV` hook with cache invalidation
- Toast notification on success/error

**CV API Enhancements**
- `getCV(cvId)` API function to fetch CV details
- `useCV(cvId)` hook for fetching single CV
- `CVDetailResponse` type for CV detail data

**Navigation Updates**
- Added "History" link to main navigation
- Route `/history` for evaluation history page
- Route `/history/:id` for CV detail page

**System Template UX Improvement**
- Added info banner on system template detail pages explaining they cannot be edited/deleted
- Clear guidance to clone template to create editable copy

### Changed

**Routes (`routes.tsx`)**
- Added `/history` route for HistoryPage
- Updated route documentation

**RootLayout (`RootLayout.tsx`)**
- Added History link to navigation bar

**CV Feature Exports (`features/cv/index.ts`)**
- Exported HistoryPage and useCVList hook

---

## [0.11.0] - 2026-02-15 📋 EVALUATION PROFILES & TEMPLATE SELECTOR

### Added

**Evaluation Profiles Feature (`features/profile/`)**
- Complete profile/template management UI for CV evaluation criteria
- `ProfilesPage` - List all evaluation profiles with search filtering
- `ProfileDetailPage` - View profile with all criteria details
- `ProfileEditPage` - Edit profile metadata and manage criteria
- `ProfileCreatePage` - Create new profile with criteria
- `ProfileCard` - Card component for profile summaries
- `ProfileList` - Grid display with system/user profile separation
- `CloneProfileModal` - Clone existing profiles with new name
- `DeleteProfileModal` - Confirmation dialog for profile deletion
- `CriterionCard` - Display individual evaluation criteria
- `CriterionForm` - Add/edit criteria with keywords support

**Template Selector (`TemplateSelector.tsx`)**
- Dropdown for selecting evaluation template before CV upload
- Grouped options (System Templates / My Templates)
- LocalStorage persistence of last selected template
- Preview of selected template info (criteria count, passing score)
- Link to Profiles page for template management
- Upload blocked until template is selected

**Modal Component (`shared/components/ui/Modal.tsx`)**
- Accessible modal/dialog component with backdrop
- Focus trap and escape key handling
- Multiple sizes (sm, md, lg, xl, 2xl)
- Animated entrance with backdrop blur
- `ModalBody` and `ModalFooter` sub-components

**Navigation**
- Added navigation links in header (Evaluate, Profiles, Settings)
- Active state highlighting for current route
- Responsive design with hidden text on mobile

### Changed

**CV Upload Flow (`CVPage.tsx`)**
- Template selection now required before uploading CVs
- Dropzone disabled until template is selected
- Warning message shown when no template selected
- Template ID passed to upload API for evaluation

**Upload API (`cv.api.ts`, `useUploadCV.ts`)**
- `uploadCV` function now accepts `templateId` parameter
- `useUploadCV` hook updated to accept `{ file, templateId }` object
- Template ID passed as query parameter to backend

**Routes (`routes.tsx`)**
- Added `/profiles` - Profiles list page
- Added `/profiles/new` - Create new profile
- Added `/profiles/:id` - View profile details
- Added `/profiles/:id/edit` - Edit profile

### API Integration

**Profile Hooks (`useProfiles.ts`)**
- `useProfiles` - Fetch all profiles
- `useProfile` - Fetch single profile with criteria
- `useCreateProfile` - Create profile mutation
- `useUpdateProfile` - Update profile mutation
- `useDeleteProfile` - Delete profile mutation
- `useCloneProfile` - Clone profile mutation
- `useAddCriterion` - Add criterion mutation
- `useUpdateCriterion` - Update criterion mutation
- `useDeleteCriterion` - Delete criterion mutation

**Profile API (`profileApi.ts`)**
- Full CRUD operations for profiles and criteria
- Clone profile endpoint support

**Zod Schemas (`profile.schemas.ts`)**
- `ProfileSummary`, `ProfileResponse`, `ProfileCreate`, `ProfileUpdate`
- `CriterionResponse`, `CriterionCreate`, `CriterionUpdate`
- `CloneProfileRequest`, `ProfileListResponse`

---

## [0.10.2] - 2026-02-15 🛡️ ERROR BOUNDARY & SETTINGS FIX

### Added

**Route Error Boundary (`ErrorBoundary.tsx`)**
- `RouteErrorBoundary` component for React Router error handling
- Beautiful error page with gradient background and icons
- Shows error details in development mode
- Action buttons: Go Back, Home Page, Reload
- Support for route error responses (404, etc.)

### Changed

**Router Configuration (`routes.tsx`)**
- Added `errorElement` prop to all routes
- Errors now show branded error page instead of React Router default

### Fixed

**Settings Page (`SettingsPage.tsx`)**
- Fixed crash when `setupStatus.missing` is undefined
- Added optional chaining: `setupStatus.missing?.join(', ')`

---

## [0.10.1] - 2026-02-14 🔒 FILE TYPE VALIDATION SECURITY

### Added

**File Type Validation (`FileDropzone.tsx`)**
- `ALLOWED_MIME_TYPES` constant - Whitelist of valid CV MIME types
- `ALLOWED_EXTENSIONS` constant - Whitelist of valid file extensions
- `isValidCVFile()` helper - Validates files by MIME type with extension fallback
- Accepts only PDF and DOCX files (blocks images, executables, scripts, etc.)

### Changed

**FileDropzone**
- Updated `accept` prop to include all valid MIME types for PDFs and Word documents
- Enhanced file validation with MIME type and extension checking
- Updated UI text to explicitly state "PDF & DOCX only"
- Improved error messages for rejected file types

### Security

- **Defense in depth**: Frontend validation + backend validation (magic bytes)
- Prevents upload of dangerous file types (images disguised as CVs, executables, scripts)
- Consistent validation between frontend and backend

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
