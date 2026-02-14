# CV Screening Agent - Frontend ⚛️

React + TypeScript frontend for AI-powered CV screening. Upload PDF resumes and view detailed AI evaluation scorecards.

**Version:** 0.10.0 | **Last Updated:** February 14, 2026

## 🎯 Features

- **Batch CV Upload**: Upload up to 10 CVs at once with review before scanning
- **Drag & Drop Upload**: Intuitive PDF upload with progress tracking
- **Real-time Evaluation**: Instant AI-powered CV scoring
- **Visual Scorecard**: Beautiful display of pass/fail status and criteria
- **Chat with AI**: Ask questions about CVs and get AI explanations
- **Compare Candidates**: Side-by-side comparison of multiple CVs
- **Authentication**: Secure login, registration, and session management
- **Settings Management**: Configure API keys and LLM preferences
- **Notification Settings**: Configure email/WhatsApp alerts with threshold
- **Dark Mode**: Full dark theme support with system preference detection
- **Toast Notifications**: Real-time feedback for all actions
- **Error Boundaries**: Graceful error handling with recovery options
- **React Router**: Client-side navigation with protected routes
- **Responsive Design**: Works on desktop and mobile

## 🏗️ Architecture

### Tech Stack
| Technology | Purpose |
|------------|---------|
| **React 19** | UI library with hooks |
| **TypeScript** | Type safety |
| **Vite** | Fast build tool & dev server |
| **React Router 7** | Client-side routing |
| **Tailwind CSS** | Utility-first styling |
| **TanStack Query** | Server state management |
| **Zustand** | Client state (auth) |
| **Axios** | HTTP client with interceptors |
| **Zod** | Schema validation |
| **CVA** | Variant-based component styling |
| **Sonner** | Toast notifications |

### Project Structure
```
frontend/src/
├── App.tsx                     # Main app with RouterProvider
├── main.tsx                    # Entry point with providers
├── index.css                   # Global styles (Tailwind + Dark Mode)
│
├── providers/                  # React providers
│   └── QueryProvider.tsx       # TanStack Query setup
│
├── router/                     # Routing (React Router 7)
│   ├── index.ts                # Barrel exports
│   ├── routes.tsx              # Route configuration
│   ├── RootLayout.tsx          # Layout with header/footer + ThemeToggle
│   └── guards/
│       └── ProtectedRoute.tsx  # Auth guard
│
├── shared/                     # Shared utilities
│   ├── api/
│   │   └── apiClient.ts        # Axios instance with auth
│   ├── components/ui/          # UI primitives (all with dark mode)
│   │   ├── Button.tsx          # 5 variants, 3 sizes
│   │   ├── Badge.tsx           # Status badges
│   │   ├── Card.tsx            # Card with sub-components
│   │   ├── Input.tsx           # Form input
│   │   ├── Select.tsx          # Dropdown select
│   │   ├── Textarea.tsx        # Multi-line input
│   │   ├── Text.tsx            # Typography (polymorphic)
│   │   ├── Heading.tsx         # h1-h6 semantic headings
│   │   ├── Spinner.tsx         # Loading indicator
│   │   ├── Container.tsx       # Layout container
│   │   ├── ProgressBar.tsx     # Linear progress
│   │   ├── Toast.tsx           # Sonner toast wrapper
│   │   ├── ErrorBoundary.tsx   # Error boundary components
│   │   └── ThemeToggle.tsx     # Dark mode toggle
│   ├── hooks/
│   │   └── useTheme.ts         # Theme management hook
│   ├── schemas/                # Zod validation
│   │   ├── auth.schemas.ts
│   │   ├── cv.schemas.ts
│   │   ├── chat.schemas.ts
│   │   ├── settings.schemas.ts
│   │   └── notification.schemas.ts
│   ├── types/                  # TypeScript types
│   └── utils/
│       └── index.ts            # cn() class merger
│
└── features/
    ├── auth/                   # Authentication
    │   ├── api/authApi.ts
    │   ├── components/
    │   │   ├── LoginForm.tsx
    │   │   ├── RegisterForm.tsx
    │   │   ├── AuthPage.tsx
    │   │   └── UserMenu.tsx
    │   ├── hooks/useAuth.ts
    │   ├── store/authStore.ts
    │   └── pages/AuthPage.tsx
    │
    ├── cv/                     # CV Screening
    │   ├── api/cv.api.ts
    │   ├── components/
    │   │   ├── FileDropzone.tsx    # Supports batch upload
    │   │   ├── CVFileList.tsx      # Staged files list
    │   │   ├── UploadProgress.tsx
    │   │   ├── Scorecard.tsx
    │   │   ├── ScoreRing.tsx
    │   │   └── CriteriaItem.tsx
    │   ├── hooks/
    │   │   ├── useUploadCV.ts
    │   │   └── useCVList.ts
    │   └── pages/CVPage.tsx
    │
    ├── chat/                   # AI Chat
    │   ├── api/chat.api.ts
    │   ├── components/
    │   │   ├── ChatPanel.tsx
    │   │   ├── ChatMessage.tsx
    │   │   ├── ExplainModal.tsx
    │   │   └── CompareCVsModal.tsx
    │   └── hooks/useChat.ts
    │
    ├── settings/               # User Settings
    │   ├── api/settings.api.ts
    │   ├── components/
    │   │   ├── ApiKeysTab.tsx
    │   │   ├── LlmPreferencesTab.tsx
    │   │   ├── SetupBanner.tsx
    │   │   └── SetupRequiredScreen.tsx
    │   ├── hooks/useSettings.ts
    │   └── pages/SettingsPage.tsx
    │
    └── notification/           # Notification Settings
        ├── api/notificationApi.ts
        ├── components/
        │   ├── NotificationSettingsPanel.tsx
        │   ├── Toggle.tsx
        │   └── ThresholdSlider.tsx
        ├── hooks/useNotificationSettings.ts
        └── pages/NotificationSettingsPage.tsx
```
        ├── hooks/useNotificationSettings.ts
        └── pages/NotificationSettingsPage.tsx
```

## 🛤️ Routes

| Path | Component | Auth Required | Description |
|------|-----------|---------------|-------------|
| `/` | `CVPage` | ✅ | Upload & evaluate CVs |
| `/settings` | `SettingsPage` | ✅ | API keys & LLM preferences |
| `/settings/notifications` | `NotificationSettingsPage` | ✅ | Notification preferences |

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎨 Design System

### Button Variants
```tsx
<Button variant="primary">Upload CV</Button>
<Button variant="secondary">Cancel</Button>
<Button variant="outline">Details</Button>
<Button variant="ghost">Dismiss</Button>
<Button variant="danger">Delete</Button>
<Button isLoading>Submitting...</Button>
```

### Badge Variants
```tsx
<Badge variant="success">Pass</Badge>
<Badge variant="error">Fail</Badge>
<Badge variant="warning">Review</Badge>
<Badge variant="info">New</Badge>
```

### Card Components
```tsx
<Card variant="elevated">
  <CardHeader>
    <CardTitle>Evaluation Result</CardTitle>
    <CardDescription>AI-powered analysis</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    <Button>View Details</Button>
  </CardFooter>
</Card>
```

### Typography
```tsx
<Heading level={1}>Page Title</Heading>
<Heading level={2}>Section Title</Heading>
<Text size="lg" weight="semibold">Large bold text</Text>
<Text size="sm" color="muted">Small muted text</Text>
```

## 🔌 API Integration

### Configuration
The API client is configured in `shared/api/apiClient.ts`:
- Base URL: `http://localhost:8000`
- Auto-attaches JWT token to requests
- Handles 401 errors with automatic logout

### Path Aliases
The project uses `@/` as an alias to `src/`:
```tsx
import { Button } from '@/shared/components/ui';
import { useAuth } from '@/features/auth/hooks';
```

## 📦 Dependencies

### Production
- `react` / `react-dom` - UI library
- `react-router-dom` - Client-side routing
- `@tanstack/react-query` - Server state
- `zustand` - Client state
- `axios` - HTTP client
- `zod` - Schema validation
- `class-variance-authority` - Component variants
- `clsx` + `tailwind-merge` - Class utilities

### Development
- `typescript` - Type checking
- `vite` - Build tool
- `tailwindcss` - CSS framework
- `eslint` - Linting
- `@types/*` - Type definitions

## 🛣️ Roadmap

### Completed ✅
- [x] File upload with drag & drop
- [x] Batch upload (up to 10 CVs with confirmation)
- [x] Upload progress tracking
- [x] Scorecard visualization
- [x] Authentication UI (login, register, logout)
- [x] Shared UI component library (Button, Card, Input, etc.)
- [x] Path aliases (@/)
- [x] React Router integration
- [x] Notification settings page
- [x] Settings page (API keys + LLM preferences)
- [x] Chat UI with "Ask AI" and "Why?" buttons
- [x] Compare CVs modal
- [x] Toast notifications (Sonner)
- [x] Error boundaries
- [x] Dark mode with system preference detection

### Planned 🔶
- [ ] Dashboard with recent CVs and stats
- [ ] CV history list with TanStack Table
- [ ] Responsive design improvements
