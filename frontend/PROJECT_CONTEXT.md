# 📋 CV Analysis Agent Frontend - Project Context

> Quick reference for AI assistants and developers.  
> Last Updated: February 2026 (v0.14.0 - BYOK Notifications)

---

## 🎯 Platform Overview

**CV Analysis Agent** is an AI-powered CV screening platform that uses Claude AI to evaluate resumes against customizable evaluation criteria. The frontend provides a clean, intuitive interface for managing evaluation profiles/templates, uploading CVs (up to 10 at once), viewing detailed evaluation scorecards, browsing CV evaluation history, chatting with AI about candidates, comparing multiple CVs, finding similar candidates using semantic search, and configuring BYOK (Bring Your Own Keys) credentials for notifications.

---

## 📊 Current Status

| Component | Progress | Notes |
|-----------|----------|-------|
| Project Setup | ✅ 100% | Vite + React + TypeScript |
| TailwindCSS | ✅ 100% | Custom configuration + Dark Mode |
| File Upload | ✅ 100% | Drag & drop + click to upload |
| **Batch Upload** | ✅ 100% | Up to 10 CVs with confirmation |
| **Template Selector** | ✅ 100% | Required before upload |
| Upload Progress | ✅ 100% | Real-time progress tracking |
| Scorecard Display | ✅ 100% | Full evaluation visualization |
| **UI Component Library** | ✅ 100% | Button, Card, Badge, Modal, etc. |
| API Client | ✅ 100% | Axios with auth interceptors |
| TanStack Query | ✅ 100% | Server state management |
| Zustand Store | ✅ 100% | Auth state persistence |
| **Authentication UI** | ✅ 100% | Login, Register, UserMenu |
| **Path Aliases** | ✅ 100% | @/ prefix for imports |
| **Project Structure** | ✅ 100% | Feature-based organization |
| **React Router** | ✅ 100% | Client-side routing |
| **Notification Settings UI** | ✅ 100% | Email/WhatsApp + BYOK SMTP/Twilio |
| **Settings Page** | ✅ 100% | API Keys + LLM Preferences |
| **Chat UI** | ✅ 100% | Ask AI, Why buttons, Chat panel |
| **Compare CVs** | ✅ 100% | Modal for comparing 2-5 CVs |
| **Toast Notifications** | ✅ 100% | Sonner integration |
| **Error Boundaries** | ✅ 100% | Graceful error handling |
| **Dark Mode** | ✅ 100% | System preference + manual toggle |
| **Evaluation Profiles** | ✅ 100% | Full CRUD for templates/criteria |
| **CV History** | ✅ 100% | List, filter, sort, delete CVs |
| **CV Detail Page** | ✅ 100% | View evaluation details |
| **CV Similarity** | ✅ 100% | Find Similar button, similarity modal |
| **CV Ranking** | ✅ 100% | Percentile badges (Top X%) |
| **Semantic Search** | ✅ 100% | AI-powered natural language search |
| **CV Comparison** | ✅ 100% | Compare 2-10 CVs side-by-side |
| **Dashboard** | ⏳ 0% | Future feature |

**Overall Progress: ~98%** (Core features complete)

---

## 🏗️ Architecture

### Tech Stack
| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | React 19 | UI library with hooks |
| Build Tool | Vite | Fast dev server & bundler |
| Language | TypeScript | Type safety |
| Styling | TailwindCSS | Utility-first CSS + Dark Mode |
| Server State | TanStack Query | Caching & mutations |
| Client State | Zustand | Auth store with persistence |
| Routing | React Router v7 | Client-side navigation |
| HTTP | Axios | API requests with interceptors |
| Validation | Zod | Schema validation & type inference |
| Variants | CVA | Class-variance-authority for components |
| Utils | clsx + tailwind-merge | Class name utilities |
| Toasts | Sonner | Toast notifications |

### Project Structure
```
frontend/src/
├── App.tsx                     # Main app component
├── main.tsx                    # Entry point with providers
├── index.css                   # Global styles (Tailwind + Dark Mode)
│
├── providers/                  # React providers
│   ├── QueryProvider.tsx       # TanStack Query setup
│   └── index.ts
│
├── router/                     # Routing configuration
│   ├── index.ts                # Barrel exports
│   ├── routes.tsx              # Route definitions (React Router)
│   ├── RootLayout.tsx          # Layout with header + ThemeToggle
│   └── guards/
│       ├── ProtectedRoute.tsx  # Auth guard component
│       └── index.ts
│
├── shared/                     # Shared utilities & components
│   ├── api/
│   │   ├── apiClient.ts        # Axios instance with auth
│   │   └── index.ts
│   ├── components/ui/          # UI primitives (CVA-based, dark mode)
│   │   ├── Button.tsx          # 5 variants, 3 sizes, loading
│   │   ├── Badge.tsx           # 5 variants, 3 sizes
│   │   ├── Card.tsx            # CardHeader, CardContent, etc.
│   │   ├── Modal.tsx           # Accessible modal with backdrop
│   │   ├── Input.tsx           # Form input with forwardRef
│   │   ├── Select.tsx          # Dropdown select
│   │   ├── Textarea.tsx        # Multi-line input
│   │   ├── Text.tsx            # Polymorphic typography
│   │   ├── Heading.tsx         # Semantic h1-h6
│   │   ├── Spinner.tsx         # Loading indicator
│   │   ├── Container.tsx       # Layout container
│   │   ├── ProgressBar.tsx     # Linear progress
│   │   ├── Toast.tsx           # Sonner wrapper
│   │   ├── ErrorBoundary.tsx   # Error boundaries
│   │   ├── ThemeToggle.tsx     # Dark mode toggle
│   │   └── index.ts            # Barrel exports
│   ├── hooks/
│   │   ├── useTheme.ts         # Theme management
│   │   └── index.ts
│   ├── schemas/                # Zod schemas
│   │   ├── auth.schemas.ts     # Auth request/response
│   │   ├── cv.schemas.ts       # CV evaluation types
│   │   ├── chat.schemas.ts     # Chat types
│   │   ├── settings.schemas.ts # Settings types
│   │   ├── notification.schemas.ts # Notification settings
│   │   ├── profile.schemas.ts  # Profile/template types
│   │   └── index.ts
│   ├── types/
│   │   └── index.ts            # Re-exported Zod types
│   └── utils/
│       └── index.ts            # cn() utility
│
└── features/
    ├── auth/                   # Authentication feature
    │   ├── api/authApi.ts
    │   ├── components/
    │   │   ├── LoginForm.tsx
    │   │   ├── RegisterForm.tsx
    │   │   ├── AuthPage.tsx
    │   │   ├── UserMenu.tsx
    │   │   └── index.ts
    │   ├── hooks/useAuth.ts
    │   ├── store/authStore.ts
    │   ├── pages/AuthPage.tsx
    │   └── index.ts
    │
    ├── cv/                     # CV Screening feature
    │   ├── api/cv.api.ts
    │   ├── components/
    │   │   ├── FileDropzone.tsx    # Supports multiple files
    │   │   ├── CVFileList.tsx      # Staged files list
    │   │   ├── TemplateSelector.tsx# Required template picker
    │   │   ├── UploadProgress.tsx
    │   │   ├── Scorecard.tsx
    │   │   ├── ScoreRing.tsx
    │   │   ├── CriteriaItem.tsx
    │   │   ├── SimilarCVsModal.tsx # Find similar CVs modal
    │   │   ├── RankingBadge.tsx    # Percentile ranking display
    │   │   ├── SemanticSearchBar.tsx # AI-powered search
    │   │   ├── CVComparisonModal.tsx # Compare CVs side-by-side
    │   │   └── index.ts
    │   ├── hooks/
    │   │   ├── useUploadCV.ts
    │   │   ├── useCVList.ts
    │   │   ├── useCV.ts            # Single CV detail
    │   │   ├── useDeleteCV.ts      # Delete CV mutation
    │   │   ├── useSimilarity.ts    # Similar CVs, ranking, compare, search
    │   │   └── index.ts
    │   ├── pages/
    │   │   ├── CVPage.tsx          # Upload page
    │   │   ├── HistoryPage.tsx     # CV evaluation history + search
    │   │   ├── CVDetailPage.tsx    # Single CV detail view
    │   │   └── index.ts
    │   └── index.ts
    │
    ├── profile/                # Evaluation Profiles feature
    │   ├── api/profileApi.ts
    │   ├── components/
    │   │   ├── ProfileCard.tsx
    │   │   ├── ProfileList.tsx
    │   │   ├── CloneProfileModal.tsx
    │   │   ├── DeleteProfileModal.tsx
    │   │   ├── CriterionCard.tsx
    │   │   ├── CriterionForm.tsx
    │   │   └── index.ts
    │   ├── hooks/useProfiles.ts
    │   ├── pages/
    │   │   ├── ProfilesPage.tsx
    │   │   ├── ProfileDetailPage.tsx
    │   │   ├── ProfileEditPage.tsx
    │   │   ├── ProfileCreatePage.tsx
    │   │   └── index.ts
    │   └── index.ts
    │
    ├── chat/                   # AI Chat feature
    │   ├── api/chat.api.ts
    │   ├── components/
    │   │   ├── ChatPanel.tsx
    │   │   ├── ChatMessage.tsx
    │   │   ├── ExplainModal.tsx
    │   │   ├── CompareCVsModal.tsx
    │   │   └── index.ts
    │   ├── hooks/useChat.ts
    │   └── index.ts
    │
    ├── settings/               # User Settings feature
    │   ├── api/settings.api.ts
    │   ├── components/
    │   │   ├── ApiKeysTab.tsx
    │   │   ├── LlmPreferencesTab.tsx
    │   │   ├── SetupBanner.tsx
    │   │   ├── SetupRequiredScreen.tsx
    │   │   └── index.ts
    │   ├── hooks/useSettings.ts
    │   ├── pages/SettingsPage.tsx
    │   └── index.ts
    │
    └── notification/           # Notification Settings feature
        ├── api/
        │   ├── notificationApi.ts
        │   └── index.ts
        ├── components/
        │   ├── NotificationSettingsPanel.tsx
        │   ├── Toggle.tsx
        │   ├── ThresholdSlider.tsx
        │   └── index.ts
        ├── hooks/
        │   ├── useNotificationSettings.ts
        │   └── index.ts
        ├── pages/
        │   ├── NotificationSettingsPage.tsx
        │   └── index.ts
        └── index.ts
```

---

## 🎨 Design System

### UI Components (CVA-based)

| Component | Variants | Features |
|-----------|----------|----------|
| **Button** | primary, secondary, outline, ghost, danger | 3 sizes, loading state |
| **Badge** | success, error, warning, info, neutral | 3 sizes |
| **Card** | default, hover, outlined | Sub-components |
| **Modal** | sm, md, lg, xl, 2xl | Focus trap, backdrop, ESC close |
| **Input** | - | label, error, helperText |
| **Select** | - | forwardRef, custom arrow |
| **Textarea** | - | forwardRef, label, error |
| **Text** | - | 4 sizes, 4 colors, polymorphic |
| **Heading** | levels 1-6 | Semantic h1-h6 |
| **Spinner** | - | 4 sizes, accessible |
| **Container** | sm, md, lg, full | Layout wrapper |
| **ProgressBar** | - | Accessible, animated |

### Color Palette
- **Primary**: Blue tones (`blue-600`, `blue-700`)
- **Success**: Green (`green-500`, `green-600`)
- **Error**: Red (`red-500`, `red-600`)
- **Warning**: Amber (`amber-500`, `amber-600`)
- **Background**: Light gray (`gray-50`, `gray-100`)
- **Card**: White with shadows

---

## 🔌 API Integration

### Configuration
```typescript
// shared/api/apiClient.ts
const API_BASE_URL = 'http://localhost:8000';
```

### Path Aliases
```typescript
// tsconfig.app.json + vite.config.ts
import { Button } from '@/shared/components/ui';
import { useAuth } from '@/features/auth/hooks';
```

### Auth Interceptors
- **Request**: Auto-attaches `Authorization: Bearer <token>`
- **Response**: 401 triggers automatic logout & redirect

### Type Definitions (Zod-inferred)
```typescript
// Types inferred from schemas - single source of truth
type CVEvaluationResponse = z.infer<typeof cvEvaluationResponseSchema>;
type UploadResponse = z.infer<typeof uploadResponseSchema>;
type User = z.infer<typeof userSchema>;
```

---

## 🛠️ Development

### Commands
```bash
npm install     # Install dependencies
npm run dev     # Start dev server (port 5173)
npm run build   # Production build
npm run preview # Preview production build
npm run lint    # Run ESLint
```

### Key Dependencies
```json
{
  "react": "^18.x",
  "@tanstack/react-query": "^5.x",
  "zustand": "^4.x",
  "axios": "^1.x",
  "zod": "^3.x",
  "class-variance-authority": "^0.7.x",
  "clsx": "^2.x",
  "tailwind-merge": "^2.x"
}
```

---

## 📋 Planned Features (Roadmap)

### Completed ✅
- [x] Settings page (API keys + LLM preferences)
- [x] Chat UI with "Ask AI" and "Why?" buttons
- [x] Compare CVs modal
- [x] Toast notifications (Sonner)
- [x] Error boundaries
- [x] Dark mode with system preference detection
- [x] Batch CV upload with confirmation (max 10)

### Next Up 🔶
- [ ] Dashboard with recent CVs and stats
- [ ] Responsive design improvements

---

## 🗺️ Routes

| Path | Component | Auth | Description |
|------|-----------|------|-------------|
| `/` | `CVPage` | ✅ | CV Upload & Evaluation |
| `/settings` | `SettingsPage` | ✅ | API Keys & LLM Preferences |
| `/settings/notifications` | `NotificationSettingsPage` | ✅ | Notification preferences |
