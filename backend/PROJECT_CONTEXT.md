# 📋 CV Analysis Agent Backend - Project Context

> Quick reference for AI assistants and developers.  
> Last Updated: February 2026 (v0.4.0 - Database Layer)

---

## 🎯 Platform Overview

**CV Analysis Agent** is an AI-powered CV screening platform that uses Claude AI to evaluate resumes against 5 modern hiring criteria. The system extracts text from PDF CVs, sends it to Claude for intelligent analysis, and returns a detailed scorecard with pass/fail recommendations.

**Target Use Case**: AI-first fintech companies screening for candidates who embrace modern development practices, including AI-assisted coding.

---

## 📊 Current Status

| Component | Progress | Notes |
|-----------|----------|-------|
| Project Setup | ✅ 100% | FastAPI + Python 3.13 |
| PDF Processing | ✅ 100% | pdfplumber extraction |
| AI Evaluation | ✅ 100% | Claude API with 5 criteria |
| CV Upload API | ✅ 100% | Single CV upload + evaluation |
| Health Check | ✅ 100% | Basic health endpoint |
| CORS Config | ✅ 100% | Frontend integration ready |
| Environment Config | ✅ 100% | pydantic-settings |
| **Authentication** | ✅ 100% | JWT + Email/Password + Google OAuth |
| **Project Structure** | ✅ 100% | Controller-Service-Model pattern |
| **Database Layer** | ✅ 100% | PostgreSQL + pgvector + SQLAlchemy |
| **API Key Storage** | ✅ 100% | AES-256 encrypted storage |
| **Evaluation Templates** | ✅ 100% | System + user templates |
| **LangChain Integration** | ⏳ 0% | Phase 3 |
| **Multi-Agent System** | ⏳ 0% | Phase 4 |
| **Notification System** | ⏳ 0% | Phase 5 - Email + WhatsApp |

**Overall Progress: ~45%** (MVP + Auth + Refactoring + Database Complete)

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
| AI | Anthropic Claude | CV evaluation & reasoning |
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
│   ├── shared/                     # Shared business logic
│   │   └── schemas/
│   │       └── base.py             # BaseResponse, ErrorResponse
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
│       └── cv/                     # CV Screening feature
│           ├── cv_routes.py        # Route definitions
│           ├── cv_controller.py    # HTTP handlers
│           ├── cv_service.py       # Orchestration service
│           ├── cv_schemas.py       # Pydantic schemas
│           └── services/
│               ├── pdf_service.py        # PDF text extraction
│               └── evaluation_service.py # Claude AI evaluation
│
├── alembic/                        # Database migrations
│   ├── env.py                      # Migration configuration
│   └── versions/                   # Migration files
│
└── docs/
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
| `POST` | `/upload` | Upload PDF & evaluate | ❌ |
| `GET` | `/health` | Health check | ❌ |

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

### Phase 2: Database Layer
- [ ] PostgreSQL with SQLAlchemy
- [ ] pgvector for embeddings
- [ ] User, CV, Evaluation models
- [ ] Alembic migrations

### Phase 3: LangChain Integration
- [ ] Document processing chain
- [ ] Structured output parsing
- [ ] Conversation chain for "Why?" explanations

### Phase 4: Multi-Agent System
- [ ] Parser Agent (PDF extraction)
- [ ] Scorer Agent (evaluation + embeddings)
- [ ] Notification Agent (alerts)

### Phase 5: Notifications
- [ ] Email notifications (SendGrid/SES)
- [ ] WhatsApp notifications (Twilio)
- [ ] Configurable thresholds
