# CV Screening Agent - Backend 🐍

FastAPI backend for AI-powered CV screening. Extracts text from PDF resumes, stores in PostgreSQL with vector embeddings, evaluates using Claude AI, and provides RAG-powered Q&A about candidates.

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [RUNBOOK.md](RUNBOOK.md) | Quick reference for all commands (server, tests, database) |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | Architecture overview and project status |
| [docs/POSTGRESQL_SETUP.md](docs/POSTGRESQL_SETUP.md) | Database installation guide |
| [docs/AI_CONCEPTS.md](docs/AI_CONCEPTS.md) | Embeddings, RAG, LangChain explained |

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **PDF Processing** | Extract text from PDF/DOCX resumes using LangChain loaders |
| **AI Evaluation** | Claude AI scores CVs against 5 criteria with detailed reasoning |
| **Vector Search** | pgvector-powered semantic search for CV content |
| **RAG Chat** | Ask questions about CVs with context-aware responses |
| **Multi-Agent System** | Coordinated agents for parsing, scoring, chat, and notifications |
| **Email Notifications** | Async SMTP notifications when CVs meet score thresholds |
| **WhatsApp Alerts** | Twilio-powered WhatsApp notifications for high-scoring candidates |
| **LangChain** | Composable chains for evaluation, embeddings, and conversation |
| **JWT Auth** | Secure registration, login, and token refresh |
| **Google OAuth** | Optional Google sign-in support |
| **PostgreSQL** | Full persistence with SQLAlchemy 2.0 async + Alembic migrations |
| **BYOK Support** | Users can bring their own API keys (encrypted storage) |

---

## 📊 Evaluation Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Education** | 15 | High School+, bootcamps, self-taught |
| **Fintech Experience** | 20 | Finance, banking, crypto, DeFi |
| **Technical Skills** | 25 | TypeScript, Python, React, FastAPI |
| **Soft Skills** | 20 | Fast learner, stress handling, teamwork |
| **AI-Native Development** | 20 | AI tools, RAG, MCP, agents |

### Pass/Fail Logic
- **PASS**: Score ≥ 60 AND 3+ criteria met (must include Technical Skills)
- **FAIL**: Score < 60 OR fewer than 3 criteria OR no Technical Skills

---

## 🏗️ Architecture

### Controller-Service-Repository Pattern
```
Request → Routes → Controller → Service → Repository → Database
              ↓          ↓           ↓           ↓
           Thin     HTTP Logic   Business    Database
                                  Logic      Operations
```

**Why this pattern?**
- **Routes**: Thin layer, only defines endpoints and wires dependencies
- **Controller**: Handles HTTP concerns (request parsing, response formatting, error handling)
- **Service**: Contains business logic, orchestrates multiple repositories
- **Repository**: Database operations only, returns domain models

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Runtime** | Python 3.13 | Server runtime |
| **Framework** | FastAPI | Async HTTP server & routing |
| **Database** | PostgreSQL 17 | Relational data storage |
| **Vector Store** | pgvector | Semantic search with embeddings |
| **ORM** | SQLAlchemy 2.0 (async) | Database models & queries |
| **Migrations** | Alembic | Schema version control |
| **AI Framework** | LangChain | Chains, prompts, RAG |
| **LLM** | Anthropic Claude | CV evaluation & chat |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic vectors |
| **Auth** | python-jose + bcrypt | JWT tokens + password hashing |
| **Encryption** | cryptography (Fernet) | AES-256 for API keys |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app entry point, router registration
│   ├── config.py                    # Pydantic Settings, environment variables
│   │
│   ├── core/                        # 🔧 Shared infrastructure
│   │   ├── security.py              # JWT creation/validation, password hashing
│   │   ├── exceptions.py            # Custom exception classes (AppException, etc.)
│   │   └── dependencies.py          # Shared FastAPI dependencies
│   │
│   ├── db/                          # 🗄️ Database layer
│   │   ├── base.py                  # SQLAlchemy Base class, TimestampMixin
│   │   ├── session.py               # Async engine, session factory, get_db_session
│   │   ├── encryption.py            # AES-256 encryption for API keys
│   │   ├── seed.py                  # Seed data (system templates)
│   │   └── models/                  # SQLAlchemy ORM models
│   │       ├── user.py              # User model (email, password, OAuth)
│   │       ├── api_key.py           # UserApiKey (encrypted BYOK keys)
│   │       ├── agent_config.py      # UserAgentConfig (per-agent settings)
│   │       ├── template.py          # EvaluationTemplate + TemplateCriterion
│   │       ├── cv.py                # CV, CVEvaluation, CVEmbedding
│   │       ├── chat.py              # ChatHistory (RAG conversations)
│   │       └── notification.py      # NotificationSettings
│   │
│   ├── langchain/                   # 🤖 LangChain AI integration
│   │   ├── config.py                # LLM/embedding factory (get_llm, get_embeddings)
│   │   ├── document_processor.py    # PDF/DOCX loading, text chunking
│   │   ├── embeddings.py            # EmbeddingService (generate & store in pgvector)
│   │   └── chains/
│   │       ├── evaluation_chain.py  # CV scoring → CVEvaluationResult (Pydantic)
│   │       └── conversation_chain.py # RAG Q&A, ExplanationChain
│   │
│   ├── agents/                      # 🤖 Multi-Agent System
│   │   ├── messages.py              # TaskType (16 types), AgentMessage, AgentResult
│   │   ├── base.py                  # AgentContext, BaseAgent abstract class
│   │   ├── tools.py                 # Shared utilities (DocumentTools, EmbeddingTools)
│   │   ├── parser_agent.py          # PDF/DOCX parsing → text extraction
│   │   ├── scorer_agent.py          # CV evaluation + embeddings
│   │   ├── chat_agent.py            # RAG conversations, explain, compare
│   │   ├── notification_agent.py    # Email/WhatsApp dispatch
│   │   └── orchestrator.py          # AgentOrchestrator (routes tasks)
│   │
│   ├── shared/                      # 📦 Shared utilities
│   │   └── schemas/
│   │       └── base.py              # BaseResponse, ErrorResponse, PaginatedResponse
│   │
│   └── features/                    # 🎯 Feature modules
│       ├── auth/                    # Authentication feature
│       │   ├── auth_routes.py       # Route definitions (/api/auth/*)
│       │   ├── auth_controller.py   # HTTP handlers (register, login, etc.)
│       │   ├── auth_service.py      # Business logic (create user, validate, etc.)
│       │   ├── auth_repository.py   # Database operations (CRUD for users)
│       │   ├── auth_schemas.py      # Pydantic schemas (request/response)
│       │   └── auth_dependencies.py # get_current_user dependency
│       │
│       └── cv/                      # CV Screening feature
│           ├── cv_routes.py         # Route definitions (/api/cv/*)
│           ├── cv_controller.py     # HTTP handlers (upload, evaluate)
│           ├── cv_service.py        # Orchestration (PDF → evaluation)
│           ├── cv_schemas.py        # Pydantic schemas
│           └── services/
│               ├── pdf_service.py         # PDF text extraction (pdfplumber)
│               └── evaluation_service.py  # Claude AI evaluation
│
│       ├── chat/                    # Chat feature (RAG Q&A)
│           ├── chat_routes.py       # Route definitions (/api/chat/*)
│           ├── chat_controller.py   # HTTP handlers
│           ├── chat_service.py      # RAG orchestration
│           ├── chat_repository.py   # Chat history operations
│           └── chat_schemas.py      # Pydantic schemas
│
│       └── notification/            # Notification feature (Email + WhatsApp)
│           ├── notification_routes.py      # Route definitions (/api/notifications/*)
│           ├── notification_controller.py  # HTTP handlers
│           ├── notification_service.py     # Dispatch orchestration
│           ├── notification_repository.py  # Settings CRUD
│           ├── email_service.py            # Async SMTP (aiosmtplib)
│           ├── whatsapp_service.py         # Twilio WhatsApp
│           └── notification_schemas.py     # Pydantic schemas
│
├── alembic/                         # 🔄 Database migrations
│   ├── env.py                       # Alembic configuration
│   └── versions/                    # Migration files
│       └── 2cf0a8d5e5c3_initial_schema.py  # Initial 10 tables
│
├── docs/                            # 📚 Documentation
│   ├── AI_CONCEPTS.md               # Embeddings, RAG, LangChain explained
│   └── POSTGRESQL_SETUP.md          # PostgreSQL + pgvector installation
│
└── requirements.txt                 # Python dependencies
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `main.py` | Creates FastAPI app, registers routers, CORS, lifespan |
| `config.py` | Loads `.env`, defines all settings with Pydantic |
| `db/session.py` | Creates async SQLAlchemy engine and session factory |
| `db/base.py` | Base model class with `id`, `created_at`, `updated_at` |
| `db/encryption.py` | Encrypts/decrypts API keys with AES-256 |
| `langchain/config.py` | Factory functions for Claude/OpenAI models |
| `langchain/embeddings.py` | Generates embeddings and stores in pgvector |
| `langchain/chains/evaluation_chain.py` | Evaluates CVs with structured Pydantic output |

---

## 🗄️ Database Schema

### Tables (10 total)

```sql
users                  -- User accounts (email, password_hash, google_id)
user_api_keys          -- Encrypted BYOK API keys (Anthropic, OpenAI)
user_agent_configs     -- Per-user agent settings (model, temperature)
evaluation_templates   -- System + user-created evaluation templates
template_criteria      -- Individual criteria within templates
cvs                    -- Uploaded CV documents (filename, text, status)
cv_evaluations         -- Evaluation results (scores, reasoning)
cv_embeddings          -- Vector embeddings for RAG (pgvector)
chat_history           -- RAG conversation history
notification_settings  -- Email/WhatsApp alert preferences
```

### Entity Relationship

```
User (1) ──────┬──────< CV (many)
               │             │
               │             └──< CVEvaluation (many)
               │             └──< CVEmbedding (many)
               │             └──< ChatHistory (many)
               │
               ├──────< UserApiKey (many)
               ├──────< UserAgentConfig (many)
               ├──────< EvaluationTemplate (many, user-created)
               └──────< NotificationSettings (one)

EvaluationTemplate (1) ──< TemplateCriterion (many)
```

### Alembic Migrations

```bash
# Generate new migration after model changes
alembic revision --autogenerate -m "add_new_field"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 🤖 LangChain Integration

### Document Processing Pipeline

```
PDF Upload → PyPDFLoader → RecursiveCharacterTextSplitter → OpenAIEmbeddings → pgvector
```

| Component | Purpose |
|-----------|---------|
| `DocumentProcessor` | High-level class for loading PDF/DOCX and chunking |
| `EmbeddingService` | Generates embeddings, stores in `cv_embeddings` table |
| `EvaluationChain` | Scores CV against criteria, returns `CVEvaluationResult` |
| `ConversationChain` | RAG-powered Q&A using retrieved CV chunks |
| `ExplanationChain` | Explains why a criterion got a specific score |

### Code Example: Using LangChain Components

```python
from app.langchain import (
    DocumentProcessor,
    EmbeddingService,
    EvaluationChain,
    ConversationChain,
)

# 1. Process uploaded PDF
processor = DocumentProcessor()
result = await processor.process_upload(file_content, "resume.pdf")
# result.full_text, result.chunks

# 2. Store embeddings in pgvector
embedding_service = EmbeddingService(session)
await embedding_service.store_cv_embeddings(cv.id, result.chunks)

# 3. Evaluate CV
eval_chain = EvaluationChain()
evaluation = await eval_chain.evaluate(
    cv_text=result.full_text,
    template_name="AI-First Fintech",
    criteria=[...],
)
# evaluation.total_score, evaluation.passed, evaluation.criteria_scores

# 4. RAG Chat
chat_chain = ConversationChain(session)
response = await chat_chain.ask(cv.id, "What is their fintech experience?")
# response.content
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 17+ with pgvector extension
- Anthropic API key
- OpenAI API key (for embeddings)

### Installation

```bash
# 1. Clone and setup virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys and database URL

# 4. Set up PostgreSQL database
createdb cv_screening_agent
psql cv_screening_agent -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Run database migrations
alembic upgrade head

# 6. Seed system templates (optional)
python -m app.db.seed

# 7. Start development server
uvicorn app.main:app --reload --port 8000
```

> 📋 See [RUNBOOK.md](RUNBOOK.md) for complete command reference.

### Environment Variables

```env
# === Required ===
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/cv_screening_agent
JWT_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key

# === Optional (with defaults) ===
CLAUDE_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=4096
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# === Email Notifications (Optional) ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=CV Screening Agent
SMTP_USE_TLS=true

# === WhatsApp Notifications (Optional) ===
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=+14155238886
```

---

## 🔌 API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/register` | Register new user | ❌ |
| `POST` | `/login` | Login with email/password | ❌ |
| `POST` | `/refresh` | Refresh access token | ❌ |
| `POST` | `/google` | Google OAuth exchange | ❌ |
| `GET` | `/me` | Get current user profile | ✅ |

### CV Screening (`/api/cv`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/upload` | Upload PDF/DOCX & evaluate | ✅ |
| `GET` | `/` | List user's CVs (paginated) | ✅ |
| `GET` | `/{cv_id}` | Get CV details with evaluation | ✅ |
| `DELETE` | `/{cv_id}` | Delete CV and related data | ✅ |
| `POST` | `/{cv_id}/re-evaluate` | Re-evaluate with different template | ✅ |
| `GET` | `/health` | Health check (LangChain status) | ❌ |

### Chat - RAG Q&A (`/api/chat`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/{cv_id}` | Ask question about CV (RAG) | ✅ |
| `GET` | `/{cv_id}` | Get chat history | ✅ |
| `DELETE` | `/{cv_id}` | Clear chat history | ✅ |
| `POST` | `/{cv_id}/explain/{criterion}` | Explain criterion score | ✅ |
| `POST` | `/compare` | Compare multiple CVs (2-5) | ✅ |

### Notifications (`/api/notifications`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Get notification settings | ✅ |
| `PUT` | `/` | Update notification settings | ✅ |
| `POST` | `/test/{channel}` | Send test notification (email/whatsapp) | ✅ |
| `GET` | `/status` | Get service configuration status | ✅ |

### Response Example

```json
{
  "success": true,
  "message": "CV evaluated successfully",
  "evaluation": {
    "status": "pass",
    "match_score": 78,
    "criteria": [
      {
        "name": "Technical Skills",
        "score": 22,
        "max_score": 25,
        "passed": true,
        "reasoning": "Strong Python and React experience"
      }
    ],
    "recommendation": "Strong Yes",
    "candidate_name": "John Doe"
  }
}
```

---

## 🧪 Testing

**283 tests** (169 unit + 114 integration) with 100% passing.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest app/tests/unit/test_cv_service.py

# Run integration tests only
pytest app/tests/integration/
```

### Test Structure

```
app/tests/
├── conftest.py              # Shared fixtures (db, client, users, CVs)
├── unit/                    # Unit tests (169 tests)
│   ├── test_auth.py         # AuthService (21 tests)
│   ├── test_profile_service.py    # ProfileService (28 tests)
│   ├── test_similarity_service.py # SimilarityService (26 tests)
│   ├── test_cv_service.py         # CVService (32 tests)
│   ├── test_chat_service.py       # ChatService (28 tests)
│   └── test_notification_service.py # NotificationService (34 tests)
└── integration/             # Integration tests (114 tests)
    ├── test_auth_api.py     # /api/auth/* (14 tests)
    ├── test_profile_api.py  # /api/profiles/* (25 tests)
    ├── test_cv_api.py       # /api/cv/* (18 tests)
    ├── test_chat_api.py     # /api/chat/* (28 tests)
    └── test_notification_api.py # /api/notifications/* (29 tests)
```

> 📋 See [RUNBOOK.md](RUNBOOK.md) for all testing commands and options.

---

## 📚 Documentation

| Resource | URL |
|----------|-----|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |
| **Runbook** | [RUNBOOK.md](RUNBOOK.md) - All commands |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) - Version history |
| **AI Concepts** | [docs/AI_CONCEPTS.md](docs/AI_CONCEPTS.md) |
| **PostgreSQL Setup** | [docs/POSTGRESQL_SETUP.md](docs/POSTGRESQL_SETUP.md) |

---

## 🛣️ Roadmap

- [x] PDF text extraction (pdfplumber)
- [x] Claude AI evaluation
- [x] JWT authentication + Google OAuth
- [x] Controller-Service-Repository refactor
- [x] PostgreSQL database + SQLAlchemy 2.0
- [x] Alembic migrations
- [x] pgvector for semantic search
- [x] LangChain integration (chains, embeddings, RAG)
- [x] Full repository layer (CV, Evaluation, Template, Chat, Embedding)
- [x] CV API endpoints with authentication
- [x] Chat endpoints for RAG Q&A (ask, explain, compare)
- [x] Multi-agent architecture (Parser, Scorer, Chat, Notification agents)
- [x] Email notifications (aiosmtplib with HTML templates)
- [x] WhatsApp notifications (Twilio API)
- [x] Hiring profiles CRUD API
- [x] Vector similarity search (similar CVs, ranking, compare)
- [x] **Backend testing complete** (283 tests: 169 unit + 114 integration)
- [ ] Frontend notification settings UI
- [ ] Semantic search dashboard
- [ ] Adaptive scoring profiles

---

## 📄 License

MIT License
