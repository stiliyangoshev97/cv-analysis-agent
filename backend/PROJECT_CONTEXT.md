# 📋 CV Analysis Agent Backend - Project Context

> Quick reference for AI assistants and developers.  
> Last Updated: February 15, 2026 (v0.11.0 - Testing Infrastructure)

---

## 🎯 Platform Overview

**CV Analysis Agent** is an AI-powered CV screening platform that uses Claude AI to evaluate resumes against customizable hiring criteria. The system extracts text from PDF/DOCX CVs, generates embeddings for semantic search, and provides RAG-powered Q&A about candidates.

**Key Features**:
- **Customizable Hiring Profiles**: Create evaluation criteria tailored to your roles
- **AI Evaluation**: Claude scores CVs against your criteria with explanations
- **RAG Chat**: Ask questions about any CV with context-aware responses
- **Multi-Channel Notifications**: Email and WhatsApp alerts for qualified candidates

---

## 📊 Current Status

| Component | Progress | Notes |
|-----------|----------|-------|
| Project Setup | ✅ 100% | FastAPI + Python 3.13 |
| PDF Processing | ✅ 100% | pdfplumber extraction |
| AI Evaluation | ✅ 100% | Claude API with customizable criteria |
| CV Upload API | ✅ 100% | Single CV upload + evaluation |
| Health Check | ✅ 100% | Basic health endpoint |
| CORS Config | ✅ 100% | Frontend integration ready |
| Environment Config | ✅ 100% | pydantic-settings |
| **Authentication** | ✅ 100% | JWT + Email/Password + Google OAuth |
| **Project Structure** | ✅ 100% | Controller-Service-Repository pattern |
| **Database Layer** | ✅ 100% | PostgreSQL + pgvector + SQLAlchemy |
| **API Key Storage** | ✅ 100% | AES-256 encrypted storage |
| **Evaluation Templates** | ✅ 100% | System + user templates |
| **LangChain Integration** | ✅ 100% | Chains, embeddings, RAG |
| **CV Feature + DB** | ✅ 100% | Full persistence with repositories |
| **Chat Endpoints (RAG Q&A)** | ✅ 100% | Ask questions, explain scores, compare CVs |
| **Multi-Agent System** | ✅ 100% | Phase 4 - 4 specialized agents + orchestrator |
| **Notification System** | ✅ 100% | Phase 5 - Email + WhatsApp via Twilio |
| **Hiring Profiles CRUD** | ✅ 100% | Phase 6.3 - Profile management API |
| **Vector Similarity Search** | ✅ 100% | Phase 6.1 - Similar CVs, ranking, compare |
| **Testing Infrastructure** | ✅ 100% | 226 tests (169 unit + 57 integration) |

**Overall Progress: ~93%** (Phases 1-5 + 6.1 + 6.3 + Testing Complete)

---

## 🏗️ Architecture

### Controller-Service-Repository Pattern
```
Request Flow: Routes → Controller → Service → Repository → Database
                ↓          ↓           ↓           ↓
              Thin    HTTP Logic   Business    Database
                                    Logic      Operations
```

### Tech Stack
| Layer | Technology | Purpose |
|-------|------------|---------|
| Runtime | Python 3.13 | Server runtime |
| Framework | FastAPI | Async HTTP server & routing |
| Database | PostgreSQL 17 + pgvector | Relational + vector storage |
| ORM | SQLAlchemy 2.0 (async) | Database models & queries |
| Migrations | Alembic | Schema version control |
| PDF Processing | pdfplumber | Text extraction from PDFs |
| AI Framework | LangChain | Chains, prompts, RAG |
| LLM Provider | Anthropic Claude | CV evaluation & reasoning |
| Embeddings | OpenAI text-embedding-3-small | Semantic search vectors |
| Validation | Pydantic | Schema validation & serialization |
| Config | pydantic-settings | Environment management |
| Auth | python-jose + bcrypt | JWT tokens + password hashing |
| Encryption | cryptography (Fernet) | AES-256 for API keys |

### Project Structure
```
backend/
├── app/
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Settings with pydantic-settings
│   │
│   ├── core/                       # Shared infrastructure
│   │   ├── security.py             # JWT utils, password hashing
│   │   ├── exceptions.py           # Custom exception classes
│   │   └── dependencies.py         # Shared FastAPI dependencies
│   │
│   ├── db/                         # Database layer
│   │   ├── base.py                 # Base class, TimestampMixin
│   │   ├── session.py              # Async engine & session
│   │   ├── encryption.py           # AES-256 for API keys
│   │   ├── seed.py                 # System template seed data
│   │   └── models/                 # SQLAlchemy models
│   │       ├── user.py             # User model
│   │       ├── api_key.py          # UserApiKey (encrypted)
│   │       ├── agent_config.py     # UserAgentConfig
│   │       ├── template.py         # EvaluationTemplate + Criterion
│   │       ├── cv.py               # CV, CVEvaluation, CVEmbedding
│   │       ├── chat.py             # ChatHistory
│   │       └── notification.py     # NotificationSettings
│   │
│   ├── langchain/                  # LangChain AI integration
│   │   ├── config.py               # LLM & embedding configuration
│   │   ├── document_processor.py   # PDF/DOCX loading & chunking
│   │   ├── embeddings.py           # Embedding generation & pgvector
│   │   └── chains/                 # LangChain chains
│   │       ├── evaluation_chain.py # CV scoring with Pydantic output
│   │       └── conversation_chain.py # RAG Q&A about CVs
│   │
│   ├── agents/                     # Multi-Agent System
│   │   ├── __init__.py             # Barrel exports
│   │   ├── messages.py             # TaskType, AgentMessage, AgentResult
│   │   ├── base.py                 # AgentContext, BaseAgent
│   │   ├── tools.py                # Shared utilities & tool classes
│   │   ├── parser_agent.py         # Document parsing agent
│   │   ├── scorer_agent.py         # Evaluation agent
│   │   ├── chat_agent.py           # RAG conversation agent
│   │   ├── notification_agent.py   # Notification dispatch agent
│   │   └── orchestrator.py         # AgentOrchestrator
│   │
│   ├── shared/                     # Shared business logic
│   │   └── schemas/
│   │       └── base.py             # BaseResponse, ErrorResponse
│   │
│   ├── tests/                      # Test suite
│   │   ├── conftest.py             # Shared fixtures
│   │   ├── unit/                   # Unit tests (isolated)
│   │   │   ├── test_similarity_service.py
│   │   │   ├── test_auth_service.py
│   │   │   └── test_profile_service.py
│   │   └── integration/            # API integration tests
│   │       ├── test_auth_api.py
│   │       ├── test_profile_api.py
│   │       └── test_cv_api.py
│   │
│   └── features/
│       ├── auth/                   # Authentication feature
│       │   ├── auth_routes.py      # Route definitions (thin)
│       │   ├── auth_controller.py  # HTTP handlers
│       │   ├── auth_service.py     # Business logic (async)
│       │   ├── auth_repository.py  # Database operations
│       │   ├── auth_schemas.py     # Pydantic schemas
│       │   └── auth_dependencies.py # get_current_user
│       │
│       ├── cv/                     # CV Screening feature
│       │   ├── __init__.py             # Barrel exports
│       │   ├── cv_routes.py            # Route definitions
│       │   ├── cv_controller.py        # HTTP handlers
│       │   ├── cv_service.py           # Orchestration + LangChain
│       │   ├── similarity_service.py   # Vector similarity search
│       │   ├── cv_repository.py        # CV CRUD operations
│       │   ├── evaluation_repository.py # Evaluation operations
│       │   ├── template_repository.py  # Template operations
│       │   ├── embedding_repository.py # Vector search operations
│       │   ├── cv_dependencies.py      # FastAPI dependencies
│       │   ├── cv_schemas.py           # Pydantic schemas
│       │   └── services/               # Legacy services
│       │       ├── pdf_service.py          # PDF text extraction
│       │       └── evaluation_service.py   # Claude AI evaluation
│       │
│       └── chat/                   # Chat feature (RAG Q&A)
│           ├── __init__.py             # Barrel exports
│           ├── chat_routes.py          # Route definitions
│           ├── chat_controller.py      # HTTP handlers
│           ├── chat_service.py         # RAG orchestration
│           ├── chat_repository.py      # Chat history operations
│           ├── chat_dependencies.py    # FastAPI dependencies
│           └── chat_schemas.py         # Pydantic schemas
│
│       └── notification/           # Notification feature (Email + WhatsApp)
│           ├── __init__.py                 # Barrel exports
│           ├── notification_routes.py      # Route definitions
│           ├── notification_controller.py  # HTTP handlers
│           ├── notification_service.py     # Dispatch orchestration
│           ├── notification_repository.py  # Settings CRUD
│           ├── notification_schemas.py     # Pydantic schemas
│           ├── notification_dependencies.py # FastAPI dependencies
│           ├── email_service.py            # Async SMTP (aiosmtplib)
│           └── whatsapp_service.py         # Twilio WhatsApp
│
│       └── profile/                # Hiring Profile feature (CRUD)
│           ├── __init__.py                 # Barrel exports
│           ├── profile_routes.py           # Route definitions (9 endpoints)
│           ├── profile_controller.py       # HTTP handlers
│           ├── profile_service.py          # Business logic + authorization
│           └── profile_schemas.py          # Pydantic schemas
│
├── alembic/                        # Database migrations
│   ├── env.py                      # Migration configuration
│   └── versions/                   # Migration files
│
└── docs/
    ├── AI_CONCEPTS.md              # Embeddings, RAG, LangChain guide
    └── POSTGRESQL_SETUP.md         # PostgreSQL installation guide
```

### Database Schema (10 Tables)
```sql
users                 -- User accounts with OAuth support
user_api_keys         -- Encrypted BYOK API keys
user_agent_configs    -- Per-user agent settings
evaluation_templates  -- System + user templates
template_criteria     -- Criteria within templates
cvs                   -- Uploaded CV documents
cv_evaluations        -- Evaluation results
cv_embeddings         -- Vector embeddings (pgvector)
chat_history          -- CV explanation conversations
notification_settings -- Alert preferences
```

---

## 📝 Evaluation Criteria (5 Total)

| Criterion | Points | Weight | Description |
|-----------|--------|--------|-------------|
| Education | 15 | 15% | High School+, bootcamps, self-taught |
| Fintech Experience | 20 | 20% | Finance, crypto, banking, DeFi |
| Technical Skills | 25 | 25% | TypeScript, Python, React, FastAPI |
| Soft Skills & Adaptability | 20 | 20% | Fast learner, stress handling, teamwork |
| AI-Native Development | 20 | 20% | AI tools, RAG, MCP, agents |

### Scoring Thresholds
- **PASS**: Score ≥ 60 AND 3+ criteria met (must include Technical Skills)
- **FAIL**: Score < 60 OR fewer than 3 criteria OR no Technical Skills

### AI-Native Development Specifics
- AI coding tools: Claude Code, GitHub Copilot, Cursor, Windsurf
- Vibe coding: AI pair programming, prompt engineering
- RAG systems: Vector databases, embeddings, retrieval
- MCP: Model Context Protocol, tool-use, function calling
- AI agents: LangChain, LlamaIndex, autonomous systems

---

## 🔌 API Endpoints

### Authentication (`/api/auth/`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/register` | Register with email/password | ❌ |
| `POST` | `/login` | Login with credentials | ❌ |
| `POST` | `/refresh` | Refresh access token | ❌ |
| `POST` | `/google` | Google OAuth exchange | ❌ |
| `GET` | `/me` | Get current user | ✅ |

### CV Screening (`/api/cv/`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/upload` | Upload PDF/DOCX & evaluate | ✅ |
| `GET` | `/` | List user's CVs (paginated) | ✅ |
| `GET` | `/{cv_id}` | Get CV details with evaluation | ✅ |
| `DELETE` | `/{cv_id}` | Delete CV and related data | ✅ |
| `POST` | `/{cv_id}/re-evaluate` | Re-evaluate with different template | ✅ |
| `GET` | `/{cv_id}/similar` | Find similar CVs | ✅ |
| `GET` | `/{cv_id}/ranking` | Get percentile ranking | ✅ |
| `POST` | `/compare` | Compare multiple CVs | ✅ |
| `POST` | `/search` | Semantic search by query | ✅ |
| `GET` | `/health` | Health check (LangChain status) | ❌ |

### Chat (`/api/chat/`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/{cv_id}` | Ask question about CV (RAG) | ✅ |
| `GET` | `/{cv_id}` | Get chat history | ✅ |
| `DELETE` | `/{cv_id}` | Clear chat history | ✅ |
| `POST` | `/{cv_id}/explain/{criterion}` | Explain criterion score | ✅ |
| `POST` | `/compare` | Compare multiple CVs | ✅ |

### Notifications (`/api/notifications/`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Get notification settings | ✅ |
| `PUT` | `/` | Update notification settings | ✅ |
| `POST` | `/test/{channel}` | Send test notification | ✅ |
| `GET` | `/status` | Get service configuration status | ✅ |

### Hiring Profiles (`/api/profiles/`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | List all profiles (system + user) | ✅ |
| `GET` | `/{profile_id}` | Get profile with criteria | ✅ |
| `POST` | `/` | Create new profile | ✅ |
| `PUT` | `/{profile_id}` | Update profile metadata | ✅ |
| `DELETE` | `/{profile_id}` | Delete user profile | ✅ |
| `POST` | `/{profile_id}/clone` | Clone a profile | ✅ |
| `POST` | `/{profile_id}/criteria` | Add criterion | ✅ |
| `PUT` | `/{profile_id}/criteria/{id}` | Update criterion | ✅ |
| `DELETE` | `/{profile_id}/criteria/{id}` | Delete criterion | ✅ |

---

## 🧪 Testing

### Test Structure
```
backend/app/tests/
├── conftest.py                     # Shared fixtures (mocked embeddings, auth)
├── unit/                           # Unit tests (isolated, mocked)
│   ├── test_similarity_service.py  # 26 tests - vector search logic
│   ├── test_auth_service.py        # 21 tests - auth flows, JWT, password
│   └── test_profile_service.py     # 28 tests - CRUD, clone, criteria
└── integration/                    # API integration tests (full stack)
    ├── test_auth_api.py            # Auth endpoints (register, login, etc.)
    ├── test_profile_api.py         # Profile endpoints (CRUD, clone)
    └── test_cv_api.py              # CV endpoints (upload, list, delete)
```

### Running Tests
```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/unit/test_auth_service.py -v

# Run only unit tests
pytest app/tests/unit/ -v

# Run only integration tests
pytest app/tests/integration/ -v
```

### Test Results (Latest)
| Category | Passed | Skipped | Notes |
|----------|--------|---------|-------|
| Unit Tests | 75 | 0 | Services fully tested |
| Integration Tests | 57 | 0 | All endpoints tested |
| **Total** | **132** | **0** | 100% passing |

### Key Testing Patterns
- **Mocked embeddings**: OpenAI embeddings are mocked in `conftest.py` to avoid API key requirement
- **Async fixtures**: Using `pytest-asyncio` with `AsyncClient` for FastAPI testing
- **Isolated database**: Each test uses a fresh in-memory SQLite database
- **Auth helpers**: Fixtures provide authenticated users and tokens for protected endpoints

---

## 🛠️ Development

### Running the Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Environment Variables
```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
CLAUDE_MODEL=claude-sonnet-4-20250514
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 📋 Planned Features (Roadmap)

### Phase 2: Database Layer ✅
- [x] PostgreSQL with SQLAlchemy
- [x] pgvector for embeddings
- [x] User, CV, Evaluation models
- [x] Alembic migrations

### Phase 3: LangChain Integration ✅
- [x] Document processing chain (PDF/DOCX)
- [x] Structured output parsing (Pydantic)
- [x] Embedding generation & storage
- [x] Conversation chain for RAG Q&A
- [x] "Why?" explanation chain

### Phase 4: Multi-Agent System ✅
- [x] Parser Agent (PDF extraction)
- [x] Scorer Agent (evaluation + embeddings)
- [x] Chat Agent (RAG conversations)
- [x] Notification Agent (alerts)
- [x] Agent Orchestrator (task routing)

### Phase 5: Notifications ✅
- [x] Email notifications (aiosmtplib)
- [x] WhatsApp notifications (Twilio)
- [x] Configurable thresholds
- [x] User preference settings

### Phase 6: Signature Features (In Progress)
- [x] **6.3 Hiring Profiles CRUD** - Profile management API
- [x] **6.1 Vector Similarity Search** - Find similar CVs, ranking, compare
- [ ] **6.4 Semantic Search** - Natural language CV search (backend done, needs frontend)
