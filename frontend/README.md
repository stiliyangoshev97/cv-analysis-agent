# CV Screening Agent - Frontend ⚛️

React + TypeScript frontend for AI-powered CV screening. Upload PDF resumes and view detailed AI evaluation scorecards.

**Version:** 0.5.0 | **Last Updated:** February 13, 2026

## 🎯 Features

- **Drag & Drop Upload**: Intuitive PDF upload with progress tracking
- **Real-time Evaluation**: Instant AI-powered CV scoring
- **Visual Scorecard**: Beautiful display of pass/fail status and criteria
- **Authentication**: Secure login, registration, and session management
- **Notification Settings**: Configure email/WhatsApp alerts with threshold
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

### Project Structure
```
frontend/src/
├── App.tsx                     # Main app with RouterProvider
├── main.tsx                    # Entry point with providers
├── index.css                   # Global styles (Tailwind)
│
├── providers/                  # React providers
│   └── QueryProvider.tsx       # TanStack Query setup
│
├── router/                     # Routing (React Router 7)
│   ├── index.ts                # Barrel exports
│   ├── routes.tsx              # Route configuration
│   ├── RootLayout.tsx          # Layout with header/footer
│   └── guards/
│       └── ProtectedRoute.tsx  # Auth guard
│
├── shared/                     # Shared utilities
│   ├── api/
│   │   └── apiClient.ts        # Axios instance with auth
│   ├── components/ui/          # UI primitives
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
│   │   └── ProgressBar.tsx     # Linear progress
│   ├── schemas/                # Zod validation
│   │   ├── auth.schemas.ts
│   │   ├── cv.schemas.ts
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
    │   │   ├── FileDropzone.tsx
    │   │   ├── UploadProgress.tsx
    │   │   ├── Scorecard.tsx
    │   │   ├── ScoreRing.tsx
    │   │   └── CriteriaItem.tsx
    │   ├── hooks/useUploadCV.ts
    │   └── pages/CVPage.tsx
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

## 🛤️ Routes

| Path | Component | Auth Required | Description |
|------|-----------|---------------|-------------|
| `/` | `CVPage` | ✅ | Upload & evaluate CVs |
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
- [x] Upload progress tracking
- [x] Scorecard visualization
- [x] Authentication UI (login, register, logout)
- [x] Shared UI component library (Button, Card, Input, etc.)
- [x] Path aliases (@/)
- [x] React Router integration
- [x] Notification settings page

### Planned 🔶
- [ ] Dashboard with recent CVs and stats
- [ ] CV history list with TanStack Table
- [ ] CV detail page with full evaluation
- [ ] Chat interface for CV Q&A
- [ ] Candidate comparison UI
- [ ] Semantic search UI
- [ ] Hiring profiles management
