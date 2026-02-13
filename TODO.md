# CV Screening Agent - TODO

## Project Elevation Roadmap

This document outlines the tasks needed to transform the MVP into a full-featured CV screening platform with authentication, database persistence, LangChain orchestration, and multi-agent architecture.

---

## 🎯 NEXT STEPS (Immediate)

> **Current Focus**: Phase 4 - Multi-Agent System

### Priority 1: Remaining Repositories ✅ COMPLETED
- [x] Create `CVRepository` - CRUD operations for CV documents
- [x] Create `EvaluationRepository` - Store/retrieve evaluations
- [x] Create `TemplateRepository` - Evaluation templates CRUD
- [x] Create `ChatRepository` - Chat history persistence
- [x] Create `EmbeddingRepository` - Vector search helpers (wraps pgvector)

### Priority 2: Integrate LangChain with CV Feature ✅ COMPLETED
- [x] Update `cv_service.py` to use `DocumentProcessor` for PDF/DOCX loading
- [x] Update `cv_service.py` to use `EvaluationChain` for scoring
- [x] Store CV in database after upload (CVRepository)
- [x] Store embeddings after processing (EmbeddingService)
- [x] Store evaluation results (EvaluationRepository)
- [x] Update `cv_controller.py` with authentication and new methods
- [x] Update `cv_routes.py` with new endpoints (list, get, delete, re-evaluate)
- [x] Add new schemas (CVSummary, CVListResponse, CVDetailResponse)

### Priority 3: Add Chat Endpoints ✅ COMPLETED
- [x] Create `features/chat/` module (separate from CV for clean separation)
- [x] Move `ChatRepository` from cv/ to chat/
- [x] Create `ChatService` - RAG orchestration (ask, explain, compare)
- [x] Create `ChatController` - HTTP handlers
- [x] Create `chat_schemas.py` - Request/response models
- [x] Create `chat_routes.py` - Route definitions
- [x] `POST /api/chat/{cv_id}` - Ask question about a CV (RAG)
- [x] `GET /api/chat/{cv_id}` - Get chat history
- [x] `DELETE /api/chat/{cv_id}` - Clear chat history
- [x] `POST /api/chat/{cv_id}/explain/{criterion}` - Explain a score
- [x] `POST /api/chat/compare` - Compare 2-5 CVs

### Priority 4: Frontend Chat UI
- [ ] Create chat components for CV detail page
- [ ] Add "Ask AI" button to evaluation results
- [ ] Add "Why?" button to each criterion score
- [ ] Implement chat history display
- [ ] Add compare CVs modal/page

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

## Phase 1.7: User Configuration System 🆕

> **Goal**: Enable users to bring their own API keys (BYOK) and create custom evaluation templates. This makes the platform open-source friendly and fully customizable.

### 1.7.1 Multi-Provider API Key System

#### Supported AI Providers
| Provider | Use Cases | Models |
|----------|-----------|--------|
| **Anthropic Claude** | Complex reasoning, CV evaluation | claude-sonnet-4-20250514, claude-3-5-haiku |
| **OpenAI GPT** | General purpose, embeddings | gpt-4o, gpt-4o-mini, text-embedding-3-small |
| **Google Gemini** | Fast parsing, cost-effective | gemini-2.0-flash, gemini-2.0-pro |
| **Groq** | Ultra-fast inference | llama-3.3-70b, mixtral-8x7b |
| **Ollama** | Local/private models | llama3, mistral, codellama |

#### Hybrid API Key Architecture
```
User Settings:
├── api_keys:                    # One key per provider (encrypted)
│   ├── claude: "sk-ant-..."
│   ├── openai: "sk-..."
│   ├── gemini: "AIza..."
│   ├── groq: "gsk_..."
│   └── ollama: "http://localhost:11434"
│
└── agent_config:                # Per-agent provider selection
    ├── parser_agent: { provider: "gemini", model: "gemini-2.0-flash" }
    ├── scorer_agent: { provider: "claude", model: "claude-sonnet-4-20250514" }
    ├── chat_agent: { provider: "openai", model: "gpt-4o" }
    └── embeddings: { provider: "openai", model: "text-embedding-3-small" }
```

#### Backend Tasks
- [ ] Create `user_api_keys` table (encrypted storage)
- [ ] Create `user_agent_config` table
- [ ] Implement AES-256 encryption for API keys
- [ ] Create API key validation service (test API call on save)
- [ ] Create provider abstraction layer (switch between Claude/GPT/Gemini/Groq/Ollama)
- [ ] `POST /api/settings/api-keys` - Add/update API key
- [ ] `GET /api/settings/api-keys` - List configured providers (masked keys)
- [ ] `DELETE /api/settings/api-keys/{provider}` - Remove API key
- [ ] `PUT /api/settings/agent-config` - Configure agent providers
- [ ] `GET /api/settings/agent-config` - Get agent configuration

#### Frontend Tasks
- [ ] Create Settings page with tabs
- [ ] Create API Keys section UI
  - [ ] Add key form with provider selector
  - [ ] Show masked keys (last 4 chars)
  - [ ] Validate on save (show success/error)
  - [ ] Delete key button with confirmation
- [ ] Create Agent Configuration section UI
  - [ ] Provider dropdown per agent
  - [ ] Model dropdown (filtered by provider)
  - [ ] "Use Defaults" button
- [ ] Create onboarding flow for first-time users
  - [ ] Welcome screen
  - [ ] API key setup (at least one required)
  - [ ] Optional agent configuration
  - [ ] Redirect to dashboard

### 1.7.2 Custom Evaluation Templates

#### Template Structure
```typescript
interface EvaluationTemplate {
  id: string;
  name: string;
  description: string;
  isSystemTemplate: boolean;
  userId: string | null;
  
  criteria: Criterion[];
  passingScore: number;          // default: 60
  minimumCriteriaMet: number;    // default: 3
  requiredCriteria: string[];    // e.g., ["technical_skills"]
}

interface Criterion {
  id: string;
  name: string;
  description: string;
  maxPoints: number;
  keywords: string[];            // AI hints
  evaluationGuidelines: string;  // Detailed instructions
}
```

#### Backend Tasks
- [ ] Create `evaluation_templates` table
- [ ] Create `template_criteria` table
- [ ] Create seed data for "AI-First Fintech" system template
- [ ] `GET /api/templates` - List templates (system + user's)
- [ ] `GET /api/templates/{id}` - Get template details
- [ ] `POST /api/templates` - Create user template
- [ ] `PUT /api/templates/{id}` - Update user template
- [ ] `DELETE /api/templates/{id}` - Delete user template
- [ ] Update CV evaluation to use selected template

#### Frontend Tasks
- [ ] Create Templates page (list view)
  - [ ] Show system templates (read-only badge)
  - [ ] Show user templates (edit/delete buttons)
  - [ ] "Create New Template" button
- [ ] Create Template Editor page
  - [ ] Template name & description inputs
  - [ ] Passing score slider (0-100)
  - [ ] Minimum criteria met input
  - [ ] Criteria list with add/remove/reorder
  - [ ] Per-criterion: name, points, description, keywords, required checkbox
  - [ ] Save/Cancel buttons
- [ ] Add template selector to CV upload page
  - [ ] Dropdown with all available templates
  - [ ] Default to "AI-First Fintech" system template

### 1.7.3 System Template: "AI-First Fintech" ⭐

> This is the default template, shipped with the app, based on our original criteria.

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Education** | 15 | High School+, bootcamps, self-taught with portfolio |
| **Fintech Experience** | 20 | Finance, banking, crypto, DeFi, fintech startups |
| **Technical Skills** | 25 | TypeScript, Python, React, Node.js, FastAPI |
| **Soft Skills & Adaptability** | 20 | Fast learner, stress handling, teamwork |
| **AI-Native Development** | 20 | AI tools (Copilot, Cursor), RAG, MCP, agents |

**Pass/Fail Logic:** Score ≥ 60 AND 3+ criteria met (must include Technical Skills)

---

## Phase 2: Database Layer (PostgreSQL + pgvector) ✅ COMPLETED

### 2.1 Database Setup ✅
- [x] Install PostgreSQL locally (PostgreSQL 17 via Homebrew)
- [x] Install `pgvector` extension
- [x] Install Python dependencies (`asyncpg`, `sqlalchemy`, `alembic`, `pgvector`, `cryptography`)
- [x] Create database connection module (`/app/db/`)
- [x] Set up Alembic for migrations
- [x] Add database URL to `.env`
- [x] Create encryption utilities for API key storage (`/app/db/encryption.py`)

### 2.2 Database Models (SQLAlchemy) ✅

#### Core Tables
- [x] `User` table (id, email, password_hash, name, auth_provider, google_id, avatar_url, is_active, is_onboarded, created_at, updated_at)

#### API Keys & Agent Config (Phase 1.7)
- [x] `UserApiKey` table (id, user_id, provider, encrypted_key, key_hint, is_active, last_validated_at, created_at, updated_at)
- [x] `UserAgentConfig` table (id, user_id, parser_provider, parser_model, scorer_provider, scorer_model, chat_provider, chat_model, embeddings_provider, embeddings_model, created_at, updated_at)

#### Evaluation Templates (Phase 1.7)
- [x] `EvaluationTemplate` table (id, user_id, name, description, is_system_template, passing_score, minimum_criteria_met, created_at, updated_at)
- [x] `TemplateCriterion` table (id, template_id, name, description, max_points, keywords, evaluation_guidelines, is_required, sort_order, created_at)

#### CV & Evaluation
- [x] `CV` table (id, user_id, filename, original_text, file_size, mime_type, status, uploaded_at, created_at, updated_at)
- [x] `CVEvaluation` table (id, cv_id, template_id, total_score, passed, status, criteria_scores, overall_reasoning, strengths, weaknesses, recommendation, evaluated_at, evaluation_duration_ms, model_used, created_at)
- [x] `CVEmbedding` table (id, cv_id, chunk_text, chunk_index, embedding vector[1536], model, created_at)

#### Chat & Notifications
- [x] `ChatHistory` table (id, user_id, cv_id, role, content, created_at)
- [x] `NotificationSettings` table (id, user_id, email_enabled, email_address, whatsapp_enabled, whatsapp_number, notify_on_pass, notify_on_fail, threshold_score, created_at, updated_at)

### 2.3 Database Migrations ✅
- [x] Create initial migration with all tables
- [x] Add pgvector extension (enabled via `CREATE EXTENSION vector`)
- [x] Create indexes for common queries (auto-generated by Alembic)
- [ ] Create vector similarity index (HNSW or IVFFlat) - *Deferred to when embeddings are used*

### 2.4 Repository Layer ⏳ (In Progress)
- [x] Create `UserRepository` (CRUD operations) - In `auth_repository.py`
- [ ] Create `CVRepository` (CRUD + search operations) - *Next Steps*
- [ ] Create `EvaluationRepository` - *Next Steps*
- [ ] Create `EmbeddingRepository` (vector search methods) - *Next Steps*
- [ ] Create `ChatRepository` - *Next Steps*
- [ ] Create `TemplateRepository` - *Next Steps*

### 2.5 Auth Feature Migration ✅
- [x] Refactor `auth_service.py` to use UserRepository
- [x] Refactor `auth_controller.py` to inject AsyncSession
- [x] Refactor `auth_dependencies.py` to use database
- [x] Refactor `auth_routes.py` to pass session to controller
- [x] Delete obsolete `auth_models.py` (in-memory UserStore)
- [x] Create seed data script for "AI-First Fintech" template

---

## Phase 3: LangChain Integration ✅ COMPLETE (Core)

> **Status**: Core LangChain module complete. Remaining: integrate with CV routes and create repositories.

### 3.1 LangChain Setup ✅
- [x] Install LangChain dependencies (`langchain`, `langchain-anthropic`, `langchain-community`)
- [x] Create LangChain module (`/app/langchain/`)
- [x] Configure Claude as the LLM provider
- [x] Set up embedding model (OpenAI text-embedding-3-small)

### 3.2 Document Processing Chain ✅
- [x] Create document loader for PDF files (PyPDFLoader)
- [x] Create document loader for DOCX files (Docx2txtLoader)
- [x] Create text splitter for large documents (RecursiveCharacterTextSplitter)
- [x] Create embedding generation chain (EmbeddingService)
- [x] Store embeddings in pgvector (CVEmbedding model)

### 3.3 Evaluation Chain ✅
- [x] Create structured output parser (PydanticOutputParser with CVEvaluationResult)
- [x] Create evaluation prompt template
- [x] Create evaluation chain with dynamic criteria
- [x] Add dynamic prompt injection for Hiring Profiles

### 3.4 Conversation Chain ✅
- [x] Create conversation retrieval chain (ConversationChain)
- [x] Create "Why?" explanation chain (ExplanationChain)
- [x] Add context retrieval from CV embeddings
- [ ] Integrate PostgreSQL chat history (ChatRepository - see Next Steps)

### 3.5 Integration with CV Feature ⏳
- [ ] Update CV service to use LangChain components
- [ ] Create remaining repositories (CV, Evaluation, Chat)
- [ ] Add chat/explanation endpoints

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

1. **Phase 1**: Authentication (Email/Password + Google OAuth) ✅ COMPLETED
2. **Phase 1.5**: Project Structure Refactoring ✅ COMPLETED
3. **Phase 1.7**: User Configuration System (API Keys + Templates) 🆕
4. **Phase 2**: Database Layer (PostgreSQL + pgvector)
5. **Phase 3**: LangChain Integration
6. **Phase 4**: Multi-Agent Architecture
7. **Phase 5**: Notification System (Email + WhatsApp)
8. **Phase 6**: Signature Features
9. **Phase 7**: Frontend Enhancements
10. **Phase 8**: Testing & Documentation

> **Note**: Phase 1.7 (User Configuration) will be implemented as part of Phase 2 (Database Layer) since it requires database persistence.

---

## Environment Variables (New)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/cv_scanner

# Encryption (for API keys)
ENCRYPTION_KEY=your-32-byte-encryption-key

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

# Default AI Provider (fallback, users should add their own)
# These are OPTIONAL - users will provide their own keys
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=AIza...
# GROQ_API_KEY=gsk_...
```

---

## Next Step

**Begin with Phase 2**: Set up PostgreSQL + pgvector and implement the database models including the new user configuration tables (API keys, agent config, evaluation templates).
