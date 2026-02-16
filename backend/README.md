# CV Analysis Agent - Backend 🐍

FastAPI backend for AI-powered CV screening. Extracts text from PDF resumes, stores in PostgreSQL with vector embeddings, evaluates using AI (Claude/GPT/Gemini), and provides RAG-powered Q&A about candidates.

**Version:** 0.17.0 | **Last Updated:** February 16, 2026

## 🔒 Security

This project uses a **Bring Your Own Keys (BYOK)** model - no API keys are stored in source code:

- ✅ **Encrypted API keys** - User keys encrypted with AES-256 (Fernet) before database storage
- ✅ **Environment variables** - All secrets loaded from `.env` (gitignored)
- ✅ **JWT authentication** - Secure token-based sessions
- ✅ **Password hashing** - bcrypt with salt
- ✅ **Rate limiting** - Prevents abuse per user/endpoint

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
| **Rate Limiting** | Tiered rate limits per user/endpoint to prevent abuse |
| **LangChain** | Composable chains for evaluation, embeddings, and conversation |
| **JWT Auth** | Secure registration, login, and token refresh |
| **Google OAuth** | Optional Google sign-in support |
| **PostgreSQL** | Full persistence with SQLAlchemy 2.0 async + Alembic migrations |
| **BYOK Support** | Users can bring their own API keys (encrypted storage) |

---

## 📊 Evaluation System

### How CV Evaluation Works

The CV evaluation system uses **dynamic Evaluation Profiles** (templates) combined with a **master AI prompt** to score candidates objectively.

#### The Evaluation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CV EVALUATION FLOW                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. USER SELECTS TEMPLATE          2. USER UPLOADS CV               │
│  ┌─────────────────────────┐       ┌─────────────────────────┐      │
│  │ "Senior Backend Dev"    │       │ candidate_resume.pdf    │      │
│  │ - 5 criteria            │       │                         │      │
│  │ - 70% pass threshold    │       │                         │      │
│  └───────────┬─────────────┘       └───────────┬─────────────┘      │
│              │                                 │                    │
│              └────────────┬────────────────────┘                    │
│                           ▼                                         │
│  3. BACKEND PARSES CV                                               │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ PDF → Text extraction (LangChain document loaders)      │        │
│  └───────────┬─────────────────────────────────────────────┘        │
│              ▼                                                      │
│  4. AI EVALUATION                                                   │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ MASTER PROMPT (hidden)                                  │        │
│  │ ├─ Scoring philosophy (0-100% scale)                    │        │
│  │ ├─ Evidence-based evaluation instructions               │        │
│  │ └─ Output format (structured JSON)                      │        │
│  │                                                         │        │
│  │ TEMPLATE DATA (from selected profile)                   │        │
│  │ ├─ Template name & description                          │        │
│  │ ├─ Passing score threshold                              │        │
│  │ └─ Criteria list (name, max_points, description)        │        │
│  │                                                         │        │
│  │ CV TEXT (parsed content)                                │        │
│  │ └─ Full resume text                                     │        │
│  └───────────┬─────────────────────────────────────────────┘        │
│              ▼                                                      │
│  5. STRUCTURED RESULT                                               │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ CVEvaluationResult                                      │        │
│  │ ├─ criteria_scores[] (score, reasoning, evidence)       │        │
│  │ ├─ total_score / percentage                             │        │
│  │ ├─ passed (true/false)                                  │        │
│  │ ├─ summary                                              │        │
│  │ ├─ strengths[] / weaknesses[]                           │        │
│  │ └─ recommendation (Strong Yes/Yes/Maybe/No/Strong No)   │        │
│  └─────────────────────────────────────────────────────────┘        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### The Master Prompt

Located in `app/langchain/chains/evaluation_chain.py`, the system prompt instructs the AI:

```
You are an expert CV/resume evaluator for a hiring team.
Your task is to objectively evaluate a candidate's CV against specific criteria.
Be thorough, fair, and provide evidence-based scoring.

**Scoring Philosophy:**
- 0-20% of max: No evidence of this skill/experience
- 21-40% of max: Minimal evidence, far below requirements
- 41-60% of max: Some evidence, partially meets requirements
- 61-80% of max: Good evidence, meets requirements
- 81-100% of max: Strong evidence, exceeds requirements
```

The AI is then provided with:
1. **Template details** - name, description, passing threshold
2. **Criteria list** - each criterion with name, max points, description, and required flag
3. **CV text** - the full parsed resume content

#### Evaluation Profiles (Templates)

Users can create custom templates or use system templates. Each template defines:

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Template identifier | "Senior Backend Developer" |
| **Description** | Role description | "For 5+ year backend engineers" |
| **Passing Score** | Minimum % to pass | 70% |
| **Criteria** | List of evaluation criteria | See below |

Each **Criterion** contains:

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Skill/experience area | "Python Expertise" |
| **Description** | What to look for | "5+ years Python, Django/FastAPI experience" |
| **Max Points** | Maximum score for this criterion | 30 |
| **Is Required** | Must score >0 to pass | true |

#### Example System Templates

The system includes 20 pre-built templates for common roles:

- Senior Backend Developer
- Frontend React Developer
- Full Stack Engineer
- DevOps/SRE Engineer
- Data Scientist
- Machine Learning Engineer
- Product Manager
- And more...

---

## 📊 Default Evaluation Criteria (Legacy)

> **Note:** These are the original hardcoded criteria. The system now uses dynamic templates (see above).

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Education** | 15 | High School+, bootcamps, self-taught |
| **Fintech Experience** | 20 | Finance, banking, crypto, DeFi |
| **Technical Skills** | 25 | TypeScript, Python, React, FastAPI |
| **Soft Skills** | 20 | Fast learner, stress handling, teamwork |
| **AI-Native Development** | 20 | AI tools, RAG, MCP, agents |

### Legacy Pass/Fail Logic
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
| **LLM** | Claude, GPT, Gemini | CV evaluation & chat (user choice) |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic vectors (required) |
| **Auth** | python-jose + bcrypt | JWT tokens + password hashing |
| **Rate Limiting** | slowapi | Request throttling per user/IP |
| **Encryption** | cryptography (Fernet) | AES-256 for API keys |

### AI Provider Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Provider Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EMBEDDINGS (Fixed)              LLM (User Choice)          │
│  ┌─────────────────────┐        ┌─────────────────────────┐ │
│  │ OpenAI              │        │ Claude (Anthropic)      │ │
│  │ text-embedding-3-*  │        │ GPT-4 (OpenAI)          │ │
│  │                     │        │ Gemini (Google)         │ │
│  └─────────────────────┘        └─────────────────────────┘ │
│         ↓                                ↓                  │
│    pgvector storage           Evaluation, Chat, Compare     │
│    (1536 dimensions)          (user selects provider)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Why OpenAI for Embeddings?**
- Consistent 1536-dimension vectors for all CVs
- No migration needed when switching LLM providers
- pgvector requires consistent embedding dimensions
- Very cheap (~$0.0001 per 1K tokens)

**Supported LLM Providers:**

| Provider | Models | Best For |
|----------|--------|----------|
| **Anthropic** | Claude Opus 4.6, Sonnet 4.5, Haiku 4.5 | Best reasoning, coding, agents |
| **OpenAI** | GPT-5.2, GPT-5, GPT-4.1 | Frontier intelligence, agentic tasks |
| **Google** | Gemini 3 Pro, Gemini 3 Flash | Multimodal, balanced performance |

### Available Models (February 2026)

#### Anthropic Claude
| Model ID | Name | Use Case |
|----------|------|----------|
| `claude-opus-4-6` | Claude Opus 4.6 | Most intelligent - complex reasoning, research |
| `claude-sonnet-4-5-20250929` | Claude Sonnet 4.5 | Best balance - daily coding, analysis |
| `claude-haiku-4-5-20251001` | Claude Haiku 4.5 | Fastest - high-volume tasks, quick responses |
| `claude-opus-4-20250514` | Claude Opus 4 | Previous gen - still excellent |
| `claude-sonnet-4-20250514` | Claude Sonnet 4 | Previous gen balanced |
| `claude-haiku-4-20250514` | Claude Haiku 4 | Previous gen fast |

#### OpenAI GPT
| Model ID | Name | Use Case |
|----------|------|----------|
| `gpt-5.2` | GPT-5.2 | Best for coding and agentic tasks |
| `gpt-5.2-pro` | GPT-5.2 Pro | Smarter, more precise responses |
| `gpt-5` | GPT-5 | Intelligent reasoning with configurable effort |
| `gpt-5-mini` | GPT-5 Mini | Faster, cost-efficient for defined tasks |
| `gpt-5-nano` | GPT-5 Nano | Fastest, most cost-efficient |
| `gpt-4.1` | GPT-4.1 | Smartest non-reasoning model |
| `o3` | o3 | Advanced reasoning model |
| `o4-mini` | o4-mini | Cost-effective reasoning |

#### Google Gemini
| Model ID | Name | Use Case |
|----------|------|----------|
| `gemini-3-pro` | Gemini 3 Pro | Most intelligent, multimodal & agentic |
| `gemini-3-flash` | Gemini 3 Flash | Balanced speed and scale |
| `gemini-2.5-pro` | Gemini 2.5 Pro | Advanced thinking, complex reasoning |
| `gemini-2.5-flash` | Gemini 2.5 Flash | Best price-performance |
| `gemini-2.5-flash-lite` | Gemini 2.5 Flash-Lite | Fastest, cost-efficient |

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
│       ├── notification/            # Notification feature (Email + WhatsApp)
│           ├── notification_routes.py      # Route definitions (/api/notifications/*)
│           ├── notification_controller.py  # HTTP handlers
│           ├── notification_service.py     # Dispatch orchestration
│           ├── notification_repository.py  # Settings CRUD
│           ├── email_service.py            # Async SMTP (aiosmtplib)
│           ├── whatsapp_service.py         # Twilio WhatsApp
│           └── notification_schemas.py     # Pydantic schemas
│
│       └── settings/                # User Settings feature (API keys + LLM config)
│           ├── settings_routes.py      # Route definitions (/api/settings/*)
│           ├── settings_controller.py  # HTTP handlers
│           ├── settings_service.py     # Key validation, encryption
│           ├── settings_repository.py  # UserApiKey, UserAgentConfig CRUD
│           └── settings_schemas.py     # Pydantic schemas
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

## ❓ Why Not FastAPI-MCP?

[FastAPI-MCP](https://github.com/tadata-org/fastapi-mcp) automatically exposes FastAPI endpoints as Model Context Protocol (MCP) tools, allowing AI agents (Claude Desktop, Cursor, etc.) to interact with your API. While powerful, we don't use it here for several reasons:

| Aspect | Our Approach | FastAPI-MCP Approach |
|--------|--------------|----------------------|
| **Target Users** | Humans via web UI | AI agents via MCP |
| **Agent System** | Internal multi-agent orchestration | External AI consuming tools |
| **Security** | JWT auth, user sessions | MCP server authentication |
| **Use Case** | Web application | AI tooling / automation |

### Our Internal Multi-Agent System

We use a **multi-agent architecture** internally for processing CVs:

```
User Request → AgentOrchestrator → [ParserAgent, ScorerAgent, ChatAgent, NotificationAgent]
```

These agents are Python classes that coordinate via message passing, not MCP tools. They're designed for CV processing workflows, not for external AI consumption.

### When FastAPI-MCP Makes Sense

FastAPI-MCP is ideal when you want:
- AI agents (Claude Desktop, Cursor) to interact with your API
- Natural language control over your application
- To expose existing endpoints as AI tools without code changes

For a traditional web app with human users, standard REST endpoints with JWT auth are more appropriate.

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
- API keys configured via Settings UI (BYOK - Bring Your Own Key)

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
# ============================================================================
# CV SCREENING AGENT - BACKEND CONFIGURATION
# ============================================================================
# This application uses BYOK (Bring Your Own Key) architecture.
# Users configure their API keys via the Settings UI, NOT in this file.
# ============================================================================

# === Database (Required) ===
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/cv_screening_agent

# === Security (Required) ===
JWT_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key-base64

# === JWT Settings (Optional, with defaults) ===
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# === Google OAuth (Optional) ===
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# === LLM Defaults (Optional, users can override in Settings UI) ===
CLAUDE_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=4096

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

### Setting Up API Keys (BYOK)

After installation, users must configure their API keys via the Settings UI:

1. **Register/Login** to the application
2. **Navigate to Settings** → API Keys
3. **Configure OpenAI key** (required for embeddings)
4. **Configure LLM key** (at least one: Anthropic, OpenAI, or Google)
5. **Select default LLM provider** (Claude recommended)

> 🔐 API keys are encrypted with AES-256 before storage in the database.

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

**312 tests** (198 unit + 114 integration) — 100% passing ✅

### Test Statistics

| Category | Tests | Coverage |
|----------|-------|----------|
| **Unit Tests** | 198 | Services, business logic |
| **Integration Tests** | 114 | API endpoints, HTTP flows |
| **Total** | **312** | ~80-90s runtime |

### Unit Tests (198)

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_auth.py` | 21 | Password hashing, JWT, registration, login |
| `test_profile_service.py` | 28 | Profile CRUD, clone, criteria management |
| `test_similarity_service.py` | 26 | Cosine similarity, ranking, CV comparison |
| `test_cv_service.py` | 32 | Process pipeline, retrieval, deletion |
| `test_chat_service.py` | 28 | RAG Q&A, history, explain, compare |
| `test_notification_service.py` | 34 | Settings, dispatch, email/WhatsApp |
| `test_settings_service.py` | 29 | API keys, LLM config, validation |

### Integration Tests (114)

| Test File | Tests | Endpoints |
|-----------|-------|-----------|
| `test_auth_api.py` | 14 | `/api/auth/*` - register, login, refresh, me |
| `test_profile_api.py` | 25 | `/api/profiles/*` - CRUD, clone, criteria |
| `test_cv_api.py` | 18 | `/api/cv/*` - list, get, delete, similar, ranking |
| `test_chat_api.py` | 28 | `/api/chat/*` - ask, history, explain, compare |
| `test_notification_api.py` | 29 | `/api/notifications/*` - settings, test, status |

### Running Tests

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
├── unit/                    # Unit tests (198 tests)
│   ├── test_auth.py         
│   ├── test_profile_service.py    
│   ├── test_similarity_service.py 
│   ├── test_cv_service.py         
│   ├── test_chat_service.py       
│   ├── test_notification_service.py 
│   └── test_settings_service.py   
└── integration/             # Integration tests (114 tests)
    ├── test_auth_api.py     
    ├── test_profile_api.py  
    ├── test_cv_api.py       
    ├── test_chat_api.py     
    └── test_notification_api.py 
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
- [x] **Backend testing complete** (312 tests: 198 unit + 114 integration)
- [x] User settings API (API keys + LLM preferences)
- [ ] Frontend notification settings UI
- [ ] Semantic search dashboard
- [ ] Adaptive scoring profiles

---

## 📄 License

MIT License
