# 📋 CV Analysis Agent Frontend - Project Context

> Quick reference for AI assistants and developers.  
> Last Updated: January 2025 (v0.1.0 - MVP Release)

---

## 🎯 Platform Overview

**CV Analysis Agent** is an AI-powered CV screening platform that uses Claude AI to evaluate resumes against customizable criteria. The frontend provides a clean, intuitive interface for uploading CVs and viewing detailed evaluation scorecards.

---

## 📊 Current Status

| Component | Progress | Notes |
|-----------|----------|-------|
| Project Setup | ✅ 100% | Vite + React + TypeScript |
| TailwindCSS | ✅ 100% | Custom configuration |
| File Upload | ✅ 100% | Drag & drop + click to upload |
| Upload Progress | ✅ 100% | Real-time progress tracking |
| Scorecard Display | ✅ 100% | Full evaluation visualization |
| Base UI Components | ✅ 100% | Button, Badge, ProgressBar |
| API Client | ✅ 100% | Axios with TypeScript |
| TanStack Query | ✅ 100% | Server state management |
| **Authentication UI** | ⏳ 0% | Phase 1 - Next up |
| **Dashboard** | ⏳ 0% | Phase 7 |
| **Candidate Match-Up** | ⏳ 0% | Phase 6 |
| **Semantic Search UI** | ⏳ 0% | Phase 6 |
| **Chat Interface** | ⏳ 0% | Phase 6 |

**Overall Progress: ~20%** (MVP Complete, Elevated Features Pending)

---

## 🏗️ Architecture

### Tech Stack
| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | React 18 | UI library |
| Build Tool | Vite | Fast dev server & bundler |
| Language | TypeScript | Type safety |
| Styling | TailwindCSS | Utility-first CSS |
| State | TanStack Query | Server state management |
| HTTP | Axios | API requests |
| Variants | CVA (class-variance-authority) | Component variants |

### Feature-Based Structure
```
frontend/src/
├── App.tsx                    # Main application component
├── main.tsx                   # Entry point with providers
├── types/
│   └── index.ts              # Shared TypeScript interfaces
├── lib/
│   └── api.ts                # Axios client & API functions
├── components/
│   └── ui/                   # Reusable UI components
│       ├── Button.tsx        # Button with CVA variants
│       ├── Badge.tsx         # Status badge component
│       ├── ProgressBar.tsx   # Linear progress indicator
│       └── index.ts          # Barrel export
└── features/
    ├── cv-upload/
    │   ├── components/
    │   │   ├── FileDropzone.tsx    # Drag & drop upload
    │   │   ├── UploadProgress.tsx  # Progress indicator
    │   │   └── index.ts
    │   ├── hooks/
    │   │   ├── useUploadCV.ts      # TanStack Query mutation
    │   │   └── index.ts
    │   └── index.ts
    └── scorecard/
        ├── components/
        │   ├── Scorecard.tsx       # Main result card
        │   ├── ScoreRing.tsx       # Circular score display
        │   ├── CriteriaItem.tsx    # Individual criterion
        │   └── index.ts
        └── index.ts
```

---

## 🎨 Design System

### Colors
- **Primary**: Blue tones for interactive elements
- **Success**: Green (#22C55E) for passed criteria
- **Error**: Red (#EF4444) for failed criteria
- **Warning**: Amber for caution states
- **Background**: Light gray (#F9FAFB) page background
- **Card**: White with subtle shadows

### Components

#### Button Variants
| Variant | Use Case |
|---------|----------|
| `primary` | Main CTA buttons |
| `secondary` | Secondary actions |
| `outline` | Tertiary actions |
| `ghost` | Subtle interactions |
| `danger` | Destructive actions |

#### Badge Variants
| Variant | Use Case |
|---------|----------|
| `success` | Pass status, met criteria |
| `error` | Fail status, unmet criteria |
| `warning` | Caution indicators |
| `info` | Informational |
| `neutral` | Default/inactive |

---

## 🔌 API Integration

### Base Configuration
```typescript
const API_BASE_URL = 'http://localhost:8000';
```

### Available Functions
| Function | Endpoint | Description |
|----------|----------|-------------|
| `uploadCV(file, onProgress)` | `POST /api/cv/upload` | Upload PDF for evaluation |

### Type Definitions
```typescript
interface CVEvaluationResponse {
  candidate_name: string;
  overall_score: number;
  pass_fail: 'pass' | 'fail';
  criteria: EvaluationCriteria[];
  overall_reasoning: string;
  recommendation: string;
}

interface EvaluationCriteria {
  name: string;
  score: number;
  max_score: number;
  met: boolean;
  reasoning: string;
}
```

---

## 🛠️ Development

### Running the Dev Server
```bash
cd frontend
npm install
npm run dev
```

### Building for Production
```bash
npm run build
npm run preview
```

### Scripts
| Script | Description |
|--------|-------------|
| `dev` | Start Vite dev server |
| `build` | Production build |
| `preview` | Preview production build |
| `lint` | Run ESLint |

---

## 📱 Current User Flow

1. **Landing**: User sees upload dropzone
2. **Upload**: User drags PDF or clicks to select
3. **Progress**: Upload progress bar appears
4. **Processing**: Loading state while AI evaluates
5. **Results**: Scorecard displays with:
   - Candidate name
   - Overall score (circular visualization)
   - Pass/Fail badge
   - Criteria breakdown
   - Detailed reasoning
   - Recommendation
6. **Retry**: User can upload new CV (replaces current result)

---

## 📋 Planned Features (Roadmap)

### Phase 1: Authentication UI
- [ ] Login page (email/password)
- [ ] Registration page
- [ ] Google OAuth button
- [ ] Zustand auth store
- [ ] Protected routes
- [ ] JWT token handling

### Phase 7: Frontend Enhancements
- [ ] Dashboard with CV history
- [ ] Candidate comparison view
- [ ] Semantic search interface
- [ ] Notification preferences
- [ ] Chat interface for CV Q&A
- [ ] Batch upload queue

---

## 🔗 Dependencies

### Production
- `react` / `react-dom` - UI framework
- `@tanstack/react-query` - Server state
- `axios` - HTTP client
- `class-variance-authority` - Component variants
- `clsx` - Class name utility

### Development
- `vite` - Build tool
- `typescript` - Type checking
- `tailwindcss` - Styling
- `postcss` / `autoprefixer` - CSS processing
- `eslint` - Linting

---

## 📚 Related Documentation

- [Main README](/README.md) - Project overview
- [TODO.md](/TODO.md) - Detailed 8-phase roadmap
- [CV-Scanner.md](/CV-Scanner.md) - Feature elevation plan
- [Backend PROJECT_CONTEXT](/backend/PROJECT_CONTEXT.md) - Backend documentation
