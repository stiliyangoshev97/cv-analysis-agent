# CV Analysis Agent - Frontend ⚛️

React + TypeScript frontend for AI-powered CV screening. Upload PDF resumes and view detailed AI evaluation scorecards.

**Version:** 0.17.2 | **Last Updated:** February 20, 2026

## 🎯 Features

- **Batch CV Upload**: Upload up to 10 CVs at once with review before scanning
- **Drag & Drop Upload**: Intuitive PDF upload with simulated progress tracking
- **Real-time Evaluation**: Instant AI-powered CV scoring
- **Visual Scorecard**: Beautiful display of pass/fail status and criteria
- **Chat with AI**: Ask questions about CVs and get AI explanations
- **Compare Candidates**: Side-by-side comparison of multiple CVs
- **Find Similar**: Semantic search to find similar candidates
- **Re-evaluate CVs**: Re-evaluate with different templates
- **Custom Templates**: Create and manage evaluation profiles
- **Authentication**: Secure login, registration, and session management
- **Settings Management**: Configure API keys and LLM preferences
- **Multi-Provider LLM Support**: Choose from Anthropic, OpenAI, or Google Gemini
- **BYOK (Bring Your Own Keys)**: Users provide their own API keys
- **Notification Settings**: Configure email/WhatsApp alerts with threshold
- **Dark Mode**: Full dark theme support with system preference detection
- **Lazy Loading**: Code-split routes for faster initial load
- **SEO Optimized**: Meta tags, favicons, PWA manifest
- **Toast Notifications**: Real-time feedback for all actions
- **Error Boundaries**: Graceful error handling with recovery options

## 🤖 Supported AI Models

The app supports multiple LLM providers. Users can choose their preferred model in Settings:

### Anthropic Claude
| Model | Best For |
|-------|----------|
| **Claude Opus 4.6** | Most intelligent - complex research, deep analysis |
| **Claude Sonnet 4.5** | Best balance - daily coding, CV analysis |
| **Claude Haiku 4.5** | Fastest - high-volume screening, quick responses |

### OpenAI GPT
| Model | Best For |
|-------|----------|
| **GPT-5.2 / Pro** | Best for coding and agentic tasks |
| **GPT-5 / Mini / Nano** | Intelligent reasoning at various speeds |
| **GPT-4.1** | Reliable non-reasoning model |

### Google Gemini
| Model | Best For |
|-------|----------|
| **Gemini 3 Pro** | Most intelligent, multimodal & agentic |
| **Gemini 3 Flash** | Balanced speed and frontier intelligence |
| **Gemini 2.5 Pro/Flash** | Advanced thinking, great price-performance |

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
| `/history` | `HistoryPage` | ✅ | View evaluation history |
| `/history/:id` | `CVDetailPage` | ✅ | CV evaluation details |
| `/profiles` | `ProfilesPage` | ✅ | Evaluation templates |
| `/profiles/new` | `ProfileCreatePage` | ✅ | Create new template |
| `/profiles/:id` | `ProfileDetailPage` | ✅ | View template details |
| `/profiles/:id/edit` | `ProfileEditPage` | ✅ | Edit template |
| `/settings` | `SettingsPage` | ✅ | API keys & LLM preferences |
| `/settings/notifications` | `NotificationSettingsPage` | ✅ | Notification preferences |
| `/settings/models` | `LlmFaqPage` | ✅ | AI model comparison guide |

## ⚡ Performance

### Code Splitting
All pages are lazy-loaded using `React.lazy()` for optimal bundle splitting:

| Chunk | Size (gzip) | Contents |
|-------|-------------|----------|
| `vendor-react` | ~30 KB | React, React-DOM, React Router |
| `vendor-query` | ~15 KB | TanStack Query |
| `vendor-ui` | ~8 KB | CVA, clsx, tailwind-merge |
| `feature-cv` | ~20 KB | CV pages (loaded on demand) |
| `feature-profile` | ~8 KB | Profile pages (loaded on demand) |
| `feature-settings` | ~37 KB | Settings pages (loaded on demand) |

### PWA Support
- Web App Manifest for installable app
- Apple Touch Icon for iOS home screen
- Theme color for mobile browsers

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
- [x] Simulated progress animation
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
- [x] CV History page with filters and sorting
- [x] CV Detail page with evaluation breakdown
- [x] Find Similar candidates (semantic search)
- [x] Re-evaluate CV with different template
- [x] Custom evaluation templates/profiles
- [x] Lazy loading with React.lazy() code splitting
- [x] SEO optimization (meta tags, favicons, PWA)
- [x] Query cache invalidation for real-time updates

✅ **All planned features complete!**
- [x] Responsive design improvements
- [x] Security headers (CSP, HSTS, etc.)
- [x] Mobile-optimized layouts

---

## 🚀 Deployment (Vercel)

The frontend is configured for deployment on Vercel with `vercel.json`.

### Security Headers

The `vercel.json` includes comprehensive security headers:

| Header | Purpose |
|--------|---------|
| `Content-Security-Policy` | Strict CSP allowing only trusted domains |
| `Strict-Transport-Security` | HSTS with 1-year max-age |
| `X-Frame-Options` | Prevent clickjacking (DENY) |
| `X-Content-Type-Options` | Prevent MIME sniffing |
| `X-XSS-Protection` | XSS filter (legacy browsers) |
| `Referrer-Policy` | Strict origin policy |
| `Permissions-Policy` | Disable unused browser features |

### Environment Variables

Set these in Vercel dashboard:

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (e.g., `https://your-app.onrender.com`) |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |

### Deploy Steps

1. Connect GitHub repo to Vercel
2. Set framework to "Vite"
3. Set root directory to `frontend`
4. Add environment variables
5. Deploy!

---

## 📱 Mobile Optimization

- **Safe area insets** for notched devices (iPhone X+)
- **Minimum touch targets** (44px) for accessibility
- **Responsive headers** with hamburger menu on mobile
- **Compact layouts** on smaller screens
- **Prevent zoom on input focus** for better UX
