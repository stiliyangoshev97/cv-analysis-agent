# 📋 CV Analysis Agent Frontend - Project Context

> Quick reference for AI assistants and developers.  
> Last Updated: February 2026 (v0.3.0 - Refactoring + UI Components)

---

## 🎯 Platform Overview

**CV Analysis Agent** is an AI-powered CV screening platform that uses Claude AI to evaluate resumes against 5 modern hiring criteria. The frontend provides a clean, intuitive interface for uploading CVs and viewing detailed evaluation scorecards.

---

## 📊 Current Status

| Component | Progress | Notes |
|-----------|----------|-------|
| Project Setup | ✅ 100% | Vite + React + TypeScript |
| TailwindCSS | ✅ 100% | Custom configuration |
| File Upload | ✅ 100% | Drag & drop + click to upload |
| Upload Progress | ✅ 100% | Real-time progress tracking |
| Scorecard Display | ✅ 100% | Full evaluation visualization |
| **UI Component Library** | ✅ 100% | Button, Card, Badge, Input, etc. |
| API Client | ✅ 100% | Axios with auth interceptors |
| TanStack Query | ✅ 100% | Server state management |
| Zustand Store | ✅ 100% | Auth state persistence |
| **Authentication UI** | ✅ 100% | Login, Register, UserMenu |
| **Path Aliases** | ✅ 100% | @/ prefix for imports |
| **Project Structure** | ✅ 100% | Feature-based organization |
| **Dashboard** | ⏳ 0% | Phase 7 |
| **Semantic Search UI** | ⏳ 0% | Phase 6 |
| **Chat Interface** | ⏳ 0% | Phase 6 |

**Overall Progress: ~35%** (MVP + Auth + Refactoring Complete)

---

## 🏗️ Architecture

### Tech Stack
| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | React 18 | UI library with hooks |
| Build Tool | Vite | Fast dev server & bundler |
| Language | TypeScript | Type safety |
| Styling | TailwindCSS | Utility-first CSS |
| Server State | TanStack Query | Caching & mutations |
| Client State | Zustand | Auth store with persistence |
| HTTP | Axios | API requests with interceptors |
| Validation | Zod | Schema validation & type inference |
| Variants | CVA | Class-variance-authority for components |
| Utils | clsx + tailwind-merge | Class name utilities |

### Project Structure
```
frontend/src/
├── App.tsx                     # Main app component
├── main.tsx                    # Entry point with providers
├── index.css                   # Global styles (Tailwind)
│
├── providers/                  # React providers
│   ├── QueryProvider.tsx       # TanStack Query setup
│   └── index.ts
│
├── router/                     # Routing configuration
│   ├── index.ts                # Route definitions
│   ├── RootLayout.tsx          # Layout with header
│   └── guards/
│       ├── ProtectedRoute.tsx  # Auth guard component
│       └── index.ts
│
├── shared/                     # Shared utilities & components
│   ├── api/
│   │   ├── apiClient.ts        # Axios instance with auth
│   │   └── index.ts
│   ├── components/ui/          # UI primitives (CVA-based)
│   │   ├── Button.tsx          # 5 variants, 3 sizes, loading
│   │   ├── Badge.tsx           # 5 variants, 3 sizes
│   │   ├── Card.tsx            # CardHeader, CardContent, etc.
│   │   ├── Input.tsx           # Form input with forwardRef
│   │   ├── Select.tsx          # Dropdown select
│   │   ├── Textarea.tsx        # Multi-line input
│   │   ├── Text.tsx            # Polymorphic typography
│   │   ├── Heading.tsx         # Semantic h1-h6
│   │   ├── Spinner.tsx         # Loading indicator
│   │   ├── Container.tsx       # Layout container
│   │   ├── ProgressBar.tsx     # Linear progress
│   │   └── index.ts            # Barrel exports
│   ├── hooks/
│   │   └── index.ts
│   ├── schemas/                # Zod schemas
│   │   ├── auth.schemas.ts     # Auth request/response
│   │   ├── cv.schemas.ts       # CV evaluation types
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
    └── cv/                     # CV Screening feature
        ├── api/cv.api.ts
        ├── components/
        │   ├── FileDropzone.tsx
        │   ├── UploadProgress.tsx
        │   ├── Scorecard.tsx
        │   ├── ScoreRing.tsx
        │   ├── CriteriaItem.tsx
        │   └── index.ts
        ├── hooks/useUploadCV.ts
        ├── pages/CVPage.tsx
        └── index.ts
```

---

## 🎨 Design System

### UI Components (CVA-based)

| Component | Variants | Features |
|-----------|----------|----------|
| **Button** | primary, secondary, outline, ghost, danger | 3 sizes, loading state |
| **Badge** | default, success, warning, error, info | 3 sizes |
| **Card** | default, bordered, elevated | Sub-components |
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

### Phase 6: Dashboard & Search
- [ ] CV history list
- [ ] Semantic search with filters
- [ ] Candidate comparison view

### Phase 7: Chat Interface
- [ ] "Why did this CV pass/fail?" explanations
- [ ] Conversational follow-up questions
- [ ] Context from CV embeddings
