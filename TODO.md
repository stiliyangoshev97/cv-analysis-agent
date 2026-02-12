# CV Screening Agent - TODO

## Project Elevation Roadmap

This document outlines the tasks needed to transform the MVP into a full-featured CV screening platform with authentication, database persistence, LangChain orchestration, and multi-agent architecture.

---

## Phase 1: Authentication System ✅ COMPLETED

### 1.1 Backend Auth Setup ✅
- [x] Install auth dependencies (`python-jose`, `bcrypt`, `email-validator`)
- [x] Create `auth` module in backend (`/app/features/auth/`)
- [x] Create User model with Pydantic schemas:
  - `id`, `email`, `password_hash`, `name`, `auth_provider` (email/google), `created_at`
- [x] Implement password hashing utilities (bcrypt direct)
- [x] Implement JWT token generation and validation
- [x] Create auth router (`/api/auth/`)

### 1.2 Email/Password Authentication ✅
- [x] `POST /api/auth/register` - Register with email + password
- [x] `POST /api/auth/login` - Login with email + password
- [x] `POST /api/auth/logout` - Invalidate token (client-side)
- [x] `GET /api/auth/me` - Get current user profile
- [x] `POST /api/auth/refresh` - Refresh JWT token

### 1.3 Google OAuth Integration ✅
- [x] Set up Google Cloud Console OAuth credentials (config ready)
- [x] `POST /api/auth/google` - Google OAuth code exchange
- [x] Link Google accounts to existing email accounts (if same email)

### 1.4 Frontend Auth ✅
- [x] Create `auth` feature module (`/features/auth/`)
- [x] Create Login page component
- [x] Create Register page component
- [x] Create auth context/store (Zustand) for user state
- [x] Create `useAuth` hook
- [x] Add protected route wrapper component
- [x] Add auth header (UserMenu with logout)
- [x] Implement token storage (localStorage via Zustand persist)
- [x] Add axios interceptor for JWT token injection

### 1.5 Documentation ✅ (Added 2026-02-12)
- [x] Add comprehensive Python docstrings (Google-style) to all backend files
- [x] Add JSDoc documentation to all frontend TypeScript files
- [x] Create Zod schemas with type inference pattern for frontend
- [x] Create CHANGELOG.md for both backend and frontend
- [x] Create PROJECT_CONTEXT.md for both backend and frontend

### 1.6 Shared UI Components ✅ (Added 2026-02-12)
- [x] Create variant-based UI components with CVA (class-variance-authority)
- [x] Button - 5 variants (primary, secondary, outline, ghost, danger), 3 sizes, loading state
- [x] Badge - 5 variants (default, success, warning, error, info), 3 sizes
- [x] Card - 3 variants (default, bordered, elevated), CardHeader, CardTitle, CardContent, CardFooter
- [x] Input - forwardRef, label, error, helperText support
- [x] Textarea - forwardRef, label, error support
- [x] Select - forwardRef, custom arrow, options array
- [x] Text - 4 sizes, 4 colors, 3 weights, polymorphic `as` prop
- [x] Heading - levels 1-6, auto semantic h1-h6 element
- [x] Spinner - 4 sizes, accessible
- [x] Container - 4 size variants (sm, md, lg, full)
- [x] ProgressBar - with accessibility attributes
- [x] Refactor existing components to use shared UI components
- [x] Add `@/` path alias for clean imports

---

## Phase 1.5: Project Structure Refactoring ✅ COMPLETED

> **Goal**: Establish a professional, scalable folder structure following the **Controller-Service-Model** pattern (inspired by Express.js best practices) for both backend and frontend.

### Architecture Pattern: Controller-Service-Model

```
Request Flow: Routes → Controller → Service → Model/External APIs
                ↓          ↓           ↓
              Thin    HTTP Logic   Business Logic
```

**Separation of Concerns:**
- **Routes** (`*.routes.py`): Route definitions only, wire up endpoints to controllers
- **Controller** (`*.controller.py`): HTTP request/response handling, input validation, error responses
- **Service** (`*.service.py`): Core business logic, database operations, external API calls
- **Model** (`*.models.py`): Database models (SQLAlchemy in Phase 2)
- **Schemas** (`*.schemas.py`): Pydantic request/response validation schemas

### Current Issues Identified

**Backend:**
- CV logic split across `routers/`, `services/`, `models/` (inconsistent with `features/auth/`)
- No separation between routes and controllers (mixed in single file)
- No `core/` folder for shared infrastructure (security, DB, exceptions)
- No `shared/` folder for common schemas and utilities
- Inconsistent naming (should use `feature.*.py` pattern)

**Frontend:**
- `cv-upload` and `scorecard` are separate features that should be unified
- `lib/` folder is too minimal (only `api.ts`)
- No `core/` folder for utilities, hooks, constants
- No `pages/` folder for route-level components
- `schemas/` and `types/` overlap at root level

---

### Phase 1.5A: Backend Refactoring ✅ COMPLETED (2026-02-12)

#### Target Structure (Controller-Service-Model Pattern)
```
backend/app/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment settings
│
├── core/                      # Shared infrastructure
│   ├── __init__.py
│   ├── security.py            # JWT utils, password hashing
│   ├── exceptions.py          # Custom exception classes
│   └── dependencies.py        # Shared FastAPI dependencies
│
├── shared/                    # Shared business logic
│   ├── __init__.py
│   └── schemas/
│       ├── __init__.py
│       └── base.py            # BaseResponse, PaginatedResponse, ErrorResponse
│
├── features/
│   ├── __init__.py
│   │
│   ├── auth/                  # Authentication feature
│   │   ├── __init__.py
│   │   ├── auth.routes.py     # Route definitions (thin)
│   │   ├── auth.controller.py # HTTP handlers
│   │   ├── auth.service.py    # Business logic
│   │   ├── auth.schemas.py    # Pydantic schemas
│   │   ├── auth.models.py     # User model (in-memory → SQLAlchemy Phase 2)
│   │   └── auth.dependencies.py # Auth-specific deps (get_current_user)
│   │
│   └── cv/                    # CV Screening feature
│       ├── __init__.py
│       ├── cv.routes.py       # Route definitions (thin)
│       ├── cv.controller.py   # HTTP handlers
│       ├── cv.service.py      # Orchestration service
│       ├── cv.schemas.py      # Pydantic schemas
│       ├── cv.models.py       # CV model (Phase 2)
│       ├── cv.dependencies.py # CV-specific deps
│       └── services/          # Specialized services
│           ├── __init__.py
│           ├── pdf_service.py     # PDF text extraction
│           └── evaluation_service.py  # AI evaluation
│
└── tests/                     # Test structure
    ├── __init__.py
    ├── conftest.py            # Shared fixtures
    ├── unit/
    │   ├── test_cv_service.py
    │   └── test_auth_service.py
    └── integration/
        ├── test_cv_endpoints.py
        └── test_auth_endpoints.py
```

#### Naming Convention
- Feature files use prefix: `auth.routes.py`, `auth.controller.py`, etc.
- Matches ExampleProject pattern for consistency across stack
- Easy to identify which feature a file belongs to

#### Tasks
- [x] Create `core/` directory structure
  - [x] Create `core/__init__.py` with exports
  - [x] Create `core/security.py` - JWT/password utilities
  - [x] Create `core/exceptions.py` - Custom exception classes
  - [x] Create `core/dependencies.py` - Shared FastAPI deps
- [x] Create `shared/` directory structure
  - [x] Create `shared/__init__.py`
  - [x] Create `shared/schemas/__init__.py`
  - [x] Create `shared/schemas/base.py` - BaseResponse, ErrorResponse, PaginatedResponse
- [x] Refactor `features/auth/` to Controller-Service-Model ✅
  - [x] Create `auth_routes.py` (thin routing only)
  - [x] Create `auth_controller.py` (extract HTTP handlers from router)
  - [x] Create `auth_service.py` (from service.py)
  - [x] Create `auth_schemas.py` (from schemas.py)
  - [x] Create `auth_models.py` (from models.py)
  - [x] Create `auth_dependencies.py` (from dependencies.py)
  - [x] Update `__init__.py` exports
  - [x] Remove old files (router.py, service.py, schemas.py, models.py, dependencies.py)
- [x] Create `features/cv/` module with Controller-Service-Model ✅
  - [x] Update `cv/__init__.py`
  - [x] Create `cv_routes.py` - Thin route definitions
  - [x] Create `cv_controller.py` - HTTP handlers
  - [x] Create `cv_service.py` - Orchestration service
  - [x] Create `cv_schemas.py` - From `models/schemas.py`
  - [x] Create `cv_dependencies.py`
  - [x] Create `cv/services/__init__.py`
  - [x] Move `services/pdf_service.py` → `cv/services/pdf_service.py`
  - [x] Move `services/evaluation_service.py` → `cv/services/evaluation_service.py`
  - [x] Remove old files (router.py, schemas.py, dependencies.py)
- [x] Update `main.py` to import from new locations ✅
- [x] Remove old directories (`routers/`, `services/`, `models/`) ✅
- [ ] Create `tests/` directory structure
- [x] Verify all endpoints work after refactoring ✅

---

### Phase 1.5B: Frontend Refactoring ✅ COMPLETED (2026-02-12)

> **Updated**: Following ExampleProject frontend structure for consistency.

#### Issues Fixed ✅
- ~~`cv-upload` and `scorecard` are separate features~~ → Merged into `features/cv/`
- ~~`lib/` folder is minimal~~ → Moved to `shared/api/`
- ~~No `providers/` folder~~ → Created with QueryProvider
- ~~No `router/` folder~~ → Created with RootLayout, guards
- ~~`schemas/` and `types/` at root level~~ → Moved to `shared/`
- ~~No `pages/` inside features~~ → Added pages to auth and cv features

#### Target Structure (Following ExampleProject)
```
frontend/src/
├── App.tsx                    # Main app component
├── main.tsx                   # Entry point
├── index.css                  # Global styles
│
├── providers/                 # React providers (NEW)
│   ├── QueryProvider.tsx      # TanStack Query provider
│   └── index.ts
│
├── router/                    # Routing (NEW)
│   ├── index.tsx              # Route definitions
│   ├── RootLayout.tsx         # Layout with Header
│   ├── guards/
│   │   ├── ProtectedRoute.tsx
│   │   └── index.ts
│   └── index.ts
│
├── shared/                    # Shared utilities & components
│   ├── api/
│   │   ├── apiClient.ts       # Axios instance (from lib/api.ts)
│   │   └── index.ts
│   ├── components/
│   │   └── ui/                # UI primitives (from /components/ui/)
│   │       ├── Badge.tsx
│   │       ├── Button.tsx
│   │       └── index.ts
│   ├── hooks/
│   │   └── index.ts
│   ├── schemas/               # Zod schemas (from /schemas/)
│   │   ├── auth.schemas.ts
│   │   ├── cv.schemas.ts
│   │   └── index.ts
│   ├── types/                 # TypeScript types (from /types/)
│   │   ├── auth.types.ts
│   │   ├── cv.types.ts
│   │   └── index.ts
│   └── utils/
│       └── index.ts
│
└── features/
    ├── auth/
    │   ├── api/
    │   ├── components/
    │   ├── hooks/
    │   ├── pages/             # NEW - Auth pages
    │   │   ├── LoginPage.tsx
    │   │   ├── RegisterPage.tsx
    │   │   └── index.ts
    │   ├── store/
    │   └── index.ts
    │
    └── cv/                    # MERGED cv-upload + scorecard
        ├── api/
        │   └── cv.api.ts
        ├── components/
        │   ├── CVUploader.tsx
        │   ├── Scorecard.tsx
        │   ├── CriteriaItem.tsx
        │   └── index.ts
        ├── hooks/
        │   └── useCVUpload.ts
        ├── pages/             # NEW - CV pages
        │   ├── CVPage.tsx     # Main CV screening page (HomePage)
        │   └── index.ts
        └── index.ts
```

#### Tasks
- [x] Create `providers/` directory
  - [x] Create `providers/QueryProvider.tsx`
  - [x] Create `providers/index.ts`
- [x] Create `router/` directory
  - [x] Create `router/index.tsx` - Route definitions
  - [x] Create `router/RootLayout.tsx` - Layout with Header
  - [x] Create `router/guards/ProtectedRoute.tsx`
  - [x] Create `router/guards/index.ts`
- [x] Create `shared/` directory structure
  - [x] Create `shared/api/apiClient.ts` - Move from lib/api.ts
  - [x] Create `shared/api/index.ts`
  - [x] Move `components/ui/` → `shared/components/ui/`
  - [x] Create `shared/hooks/index.ts`
  - [x] Move `schemas/` → `shared/schemas/`
  - [x] Move `types/` → `shared/types/`
  - [x] Create `shared/utils/index.ts`
- [x] Refactor `features/auth/`
  - [x] Create `features/auth/pages/AuthPage.tsx`
  - [x] Create `features/auth/pages/index.ts`
  - [x] Update `features/auth/index.ts` with barrel exports
- [x] Create `features/cv/` (merge cv-upload + scorecard)
  - [x] Create `features/cv/api/cvApi.ts`
  - [x] Create `features/cv/api/index.ts`
  - [x] Move `cv-upload/components/` → `features/cv/components/`
  - [x] Move `scorecard/components/` → `features/cv/components/`
  - [x] Create `features/cv/components/index.ts`
  - [x] Move `cv-upload/hooks/` → `features/cv/hooks/`
  - [x] Create `features/cv/hooks/index.ts`
  - [x] Create `features/cv/pages/CVPage.tsx`
  - [x] Create `features/cv/pages/index.ts`
  - [x] Create `features/cv/index.ts` with barrel exports
- [x] Update `App.tsx` to use new structure
- [x] Update `main.tsx` if needed
- [x] Remove old directories
  - [x] Remove `lib/`
  - [x] Remove `components/` (moved to shared)
  - [x] Remove `schemas/` (moved to shared)
  - [x] Remove `types/` (moved to shared)
  - [x] Remove `features/cv-upload/`
  - [x] Remove `features/scorecard/`
- [x] Update all import paths
- [x] Verify app works after refactoring ✅ Build passes

---

## Phase 2: Database Layer (PostgreSQL + pgvector)

### 2.1 Database Setup
- [ ] Install PostgreSQL locally or set up cloud instance
- [ ] Install `pgvector` extension
- [ ] Install Python dependencies (`asyncpg`, `sqlalchemy`, `alembic`, `pgvector`)
- [ ] Create database connection module (`/app/db/`)
- [ ] Set up Alembic for migrations
- [ ] Add database URL to `.env`

### 2.2 Database Models (SQLAlchemy)
- [ ] `User` table (id, email, password_hash, name, auth_provider, notification_preferences, created_at)
- [ ] `CV` table (id, user_id, filename, original_text, upload_date, status)
- [ ] `CVEvaluation` table (id, cv_id, score, status, reasoning, criteria_json, evaluated_at)
- [ ] `CVEmbedding` table (id, cv_id, embedding vector[1536], created_at)
- [ ] `HiringProfile` table (id, user_id, name, prompt_template, criteria_config, created_at)
- [ ] `ChatHistory` table (id, user_id, cv_id, role, message, created_at)
- [ ] `NotificationSettings` table (id, user_id, email_enabled, whatsapp_enabled, whatsapp_number, threshold_score)

### 2.3 Database Migrations
- [ ] Create initial migration with all tables
- [ ] Add pgvector extension migration
- [ ] Create indexes for common queries
- [ ] Create vector similarity index (HNSW or IVFFlat)

### 2.4 Repository Layer
- [ ] Create `UserRepository` (CRUD operations)
- [ ] Create `CVRepository` (CRUD + search operations)
- [ ] Create `EvaluationRepository`
- [ ] Create `EmbeddingRepository` (vector search methods)
- [ ] Create `ChatRepository`

---

## Phase 3: LangChain Integration

### 3.1 LangChain Setup
- [ ] Install LangChain dependencies (`langchain`, `langchain-anthropic`, `langchain-community`)
- [ ] Create LangChain module (`/app/langchain/`)
- [ ] Configure Claude as the LLM provider
- [ ] Set up embedding model (Claude or OpenAI embeddings)

### 3.2 Document Processing Chain
- [ ] Create document loader for PDF files
- [ ] Create document loader for DOCX files
- [ ] Create text splitter for large documents
- [ ] Create embedding generation chain
- [ ] Store embeddings in pgvector

### 3.3 Evaluation Chain
- [ ] Create structured output parser (matches Zod schemas)
- [ ] Create evaluation prompt template
- [ ] Create evaluation chain with 3 criteria
- [ ] Add dynamic prompt injection for Hiring Profiles

### 3.4 Conversation Chain
- [ ] Create conversation retrieval chain
- [ ] Integrate PostgreSQL chat history
- [ ] Create "Why?" explanation chain
- [ ] Add context retrieval from CV embeddings

---

## Phase 4: Multi-Agent Architecture

### 4.1 Agent Framework Setup
- [ ] Design agent communication protocol
- [ ] Create base Agent class
- [ ] Create agent orchestrator/supervisor

### 4.2 Parser Agent
- [ ] Extracts and cleans text from uploaded documents
- [ ] Handles PDF, DOCX formats
- [ ] Normalizes text for consistent processing
- [ ] Outputs structured document data

### 4.3 Scorer Agent
- [ ] Receives parsed document from Parser Agent
- [ ] Runs evaluation against criteria
- [ ] Generates embeddings for vector storage
- [ ] Outputs evaluation results + embeddings

### 4.4 Notification Agent
- [ ] Monitors evaluation results
- [ ] Checks score against user's threshold
- [ ] Determines notification channels (email/WhatsApp/both)
- [ ] Dispatches notifications asynchronously

### 4.5 Chat Agent
- [ ] Handles conversational queries about CVs
- [ ] Retrieves relevant context from vector store
- [ ] Provides explanations for scores
- [ ] Maintains conversation history

---

## Phase 5: Notification System

### 5.1 Notification Preferences
- [ ] Add notification settings to user profile
- [ ] Create settings UI in frontend (email/WhatsApp/both toggle)
- [ ] Store WhatsApp number in user profile
- [ ] Store threshold score for alerts (default: 80)

### 5.2 Email Notifications
- [ ] Install email dependencies (`fastapi-mail` or `aiosmtplib`)
- [ ] Set up SMTP configuration in `.env`
- [ ] Create email templates (HTML) for high-score alerts
- [ ] Create `EmailNotificationService`
- [ ] Implement async email sending

### 5.3 WhatsApp Notifications (WhatsApp Business API)
- [ ] Set up WhatsApp Business API account
- [ ] Add WhatsApp API credentials to `.env`
- [ ] Create `WhatsAppNotificationService`
- [ ] Create message templates for high-score alerts
- [ ] Implement async WhatsApp sending

### 5.4 Background Task Integration
- [ ] Create FastAPI background task for notifications
- [ ] Implement notification dispatch logic:
  - If `score >= threshold`:
    - If `email_enabled`: Send email
    - If `whatsapp_enabled`: Send WhatsApp
    - If both: Send both

---

## Phase 6: Signature Features

### 6.1 Candidate Match-Up (Cross-CV Comparison)
- [ ] Create vector similarity search endpoint
- [ ] `POST /api/cv/compare` - Compare CV against database
- [ ] Calculate percentile ranking
- [ ] Create comparison UI component
- [ ] Show "Top X% of candidates" badge

### 6.2 Explainable Scoring (Conversational Deep-Dive)
- [ ] Create chat endpoint `POST /api/cv/{id}/chat`
- [ ] Create chat UI component with message history
- [ ] Add "Why?" button to scorecard
- [ ] Implement context-aware responses
- [ ] Store chat history in database

### 6.3 Adaptive Scoring Persona (Hiring Profiles)
- [ ] Create hiring profiles CRUD endpoints
- [ ] `GET /api/profiles` - List user's profiles
- [ ] `POST /api/profiles` - Create new profile
- [ ] `PUT /api/profiles/{id}` - Update profile
- [ ] `DELETE /api/profiles/{id}` - Delete profile
- [ ] Create profile selector in upload UI
- [ ] Inject profile prompt into evaluation chain

### 6.4 Semantic Search Dashboard
- [ ] Create semantic search endpoint `GET /api/cv/search?q=`
- [ ] Implement natural language to vector query
- [ ] Create search UI with TanStack Table
- [ ] Add filters (date range, score range, status)
- [ ] Display similarity scores in results

---

## Phase 7: Frontend Enhancements

### 7.1 Dashboard
- [ ] Create dashboard page (landing after login)
- [ ] Show recent evaluations
- [ ] Show quick stats (total CVs, avg score, pass rate)
- [ ] Add quick upload widget

### 7.2 CV History
- [ ] Create CV list page with TanStack Table
- [ ] Add sorting, filtering, pagination
- [ ] Add bulk actions (delete, re-evaluate)
- [ ] Show evaluation status badges

### 7.3 Settings Page
- [ ] Create settings page
- [ ] Notification preferences section
- [ ] Hiring profiles management section
- [ ] Account settings (change password, link Google)

### 7.4 Routing
- [ ] Install React Router
- [ ] Set up route structure:
  - `/login` - Login page
  - `/register` - Register page
  - `/` - Dashboard (protected)
  - `/upload` - Upload CV (protected)
  - `/cv/:id` - CV detail + chat (protected)
  - `/search` - Semantic search (protected)
  - `/settings` - User settings (protected)

---

## Phase 8: Testing & Documentation

### 8.1 Backend Testing
- [ ] Set up pytest
- [ ] Write unit tests for services
- [ ] Write integration tests for API endpoints
- [ ] Write tests for auth flows
- [ ] Write tests for multi-agent system

### 8.2 Frontend Testing
- [ ] Set up Vitest
- [ ] Write component tests
- [ ] Write hook tests
- [ ] Write integration tests

### 8.3 Documentation
- [ ] Update main README.md with new architecture
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Document environment variables
- [ ] Create deployment guide

---

## Priority Order

1. **Phase 1**: Authentication (Email/Password + Google OAuth)
2. **Phase 2**: Database Layer (PostgreSQL + pgvector)
3. **Phase 3**: LangChain Integration
4. **Phase 4**: Multi-Agent Architecture
5. **Phase 5**: Notification System (Email + WhatsApp)
6. **Phase 6**: Signature Features
7. **Phase 7**: Frontend Enhancements
8. **Phase 8**: Testing & Documentation

---

## Environment Variables (New)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/cv_scanner

# Auth
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_ACCESS_TOKEN=your-access-token

# Embeddings
EMBEDDING_MODEL=text-embedding-3-small
```

---

## Starting Point

**Begin with Phase 1.1**: Install auth dependencies and create the auth module structure in the backend.
