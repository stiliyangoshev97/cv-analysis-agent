# Changelog

All notable changes to the CV Analysis Agent backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.8.0] - 2026-02-13 🤖 MULTI-AGENT ARCHITECTURE (Phase 4)

### Added

**Multi-Agent System (`app/agents/`)** - Coordinated agent architecture
- `messages.py` - Agent communication protocol
  - `TaskType` enum: 16 task types across 5 categories
  - `AgentStatus` enum: PENDING, RUNNING, SUCCESS, FAILED, SKIPPED
  - `AgentMessage` dataclass: Input with payload and metadata
  - `AgentResult` dataclass: Output with chaining support (next_task)
- `base.py` - Agent foundation
  - `AgentContext`: Dependency injection with all repositories
  - `BaseAgent`: Abstract base class with execute/process pattern
- `tools.py` - Shared utilities
  - `validate_file()`, `extract_candidate_name()`, `format_criteria_results()`
  - `DocumentTools`, `EmbeddingTools`, `EvaluationTools`, `ConversationTools`

**Specialized Agents**
- `parser_agent.py` - Document parsing (PDF/DOCX)
  - Tasks: `PARSE_DOCUMENT`, `EXTRACT_TEXT`
  - Chains to ScorerAgent via `next_task`
- `scorer_agent.py` - Evaluation and embeddings
  - Tasks: `EVALUATE_CV`, `GENERATE_EMBEDDINGS`, `RE_EVALUATE`
  - Creates CV records, stores embeddings, runs evaluation
- `chat_agent.py` - RAG conversations
  - Tasks: `ASK_QUESTION`, `EXPLAIN_SCORE`, `COMPARE_CVS`
  - Tasks: `GET_CHAT_HISTORY`, `CLEAR_CHAT_HISTORY`
- `notification_agent.py` - Alerts (stub for Phase 5)
  - Tasks: `CHECK_THRESHOLD`, `SEND_EMAIL`, `SEND_WHATSAPP`, `DISPATCH_NOTIFICATION`

**Orchestrator**
- `orchestrator.py` - Central coordinator
  - `AgentOrchestrator`: Routes tasks to appropriate agents
  - `WorkflowResult`: Aggregates multi-step results
  - Convenience methods: `upload_cv()`, `ask_question()`, `re_evaluate()`
  - Task chaining with `next_task` support
  - Maximum chain depth protection (10 steps)

### Architecture

```
AgentOrchestrator (Supervisor/Router)
       │
┌──────┼──────┬──────────┬────────────┐
▼      ▼      ▼          ▼            ▼
Parser  Scorer  Chat   Notification   ...
Agent   Agent   Agent     Agent

Workflow Example (CV Upload):
  PARSE_DOCUMENT → EVALUATE_CV → CHECK_THRESHOLD → DISPATCH_NOTIFICATION
```

### Technical Details
- 4 specialized agents + 1 orchestrator
- 16 task types organized by category
- Shared `AgentContext` for dependency injection
- Built-in timing and error handling in base class
- Task chaining via `next_task` in `AgentResult`
- Maximum 10-step chain depth for safety

---

## [0.7.0] - 2026-02-13 💬 CHAT FEATURE (RAG Q&A)

### Added

**Chat Feature (`app/features/chat/`)** - New standalone feature module
- `ChatRepository` - Chat history database operations (moved from cv/)
  - `add_message()`, `add_user_message()`, `add_assistant_message()`
  - `get_conversation()`, `get_recent_messages()`, `count_messages()`
  - `clear_conversation()`, `get_conversations_summary()`
- `ChatService` - RAG orchestration service
  - `ask()` - Full RAG pipeline (retrieve context → generate response → persist)
  - `get_history()` - Get chat history with ownership check
  - `clear_history()` - Clear conversation for a CV
  - `explain_criterion()` - Generate detailed score explanation
  - `compare_cvs()` - Compare 2-5 CVs against each other
- `ChatController` - HTTP handlers for all chat endpoints
- `ChatSchemas` - Pydantic schemas:
  - `ChatMessageRequest`, `ChatMessageResponse`, `ChatHistoryResponse`
  - `ExplainCriterionRequest`, `ExplainCriterionResponse`
  - `CompareRequest`, `CompareResponse`, `AskResponse`

**New API Endpoints (`/api/chat`)**
- `POST /api/chat/{cv_id}` - Ask question about CV (RAG)
- `GET /api/chat/{cv_id}` - Get chat history
- `DELETE /api/chat/{cv_id}` - Clear chat history
- `POST /api/chat/{cv_id}/explain/{criterion}` - Explain criterion score
- `POST /api/chat/compare` - Compare multiple CVs

### Changed
- Moved `chat_repository.py` from `features/cv/` to `features/chat/`
- Updated `features/__init__.py` to export `chat_router`
- Updated `main.py` to include chat router at `/api/chat`

### Technical Details
- Clean feature separation (chat is independent module)
- Full RAG pipeline: embed question → vector search → context injection → LLM
- Cross-CV comparison support (2-5 CVs)
- Conversation history maintained per CV per user
- Uses `ConversationChain` and `ExplanationChain` from langchain module

---

## [0.6.0] - 2026-02-13 🔗 CV FEATURE DATABASE INTEGRATION

### Added

**CV Repositories (`app/features/cv/`)**
- `CVRepository` - CRUD operations for CV documents
  - `create()`, `get_by_id()`, `get_by_user()`, `count_by_user()`
  - `update_status()`, `update_candidate_name()`, `delete()`
  - `get_by_status()` - Batch processing helper
- `EvaluationRepository` - Evaluation results operations
  - `create()`, `get_by_id()`, `get_by_cv()`, `get_latest_by_cv()`
  - `get_by_template()`, `get_by_status()`, `count_by_cv()`
- `TemplateRepository` - Template and criteria operations
  - `get_by_id()`, `get_with_criteria()`, `get_by_name()`
  - `get_system_templates()`, `get_by_user()`, `get_available_for_user()`
  - `get_default_template()`, CRUD for templates and criteria
  - Protection for system templates (cannot update/delete)
- `ChatRepository` - Chat history operations
  - `add_message()`, `add_user_message()`, `add_assistant_message()`
  - `get_conversation()`, `get_recent_messages()`, `count_messages()`
  - `clear_conversation()`, `get_conversations_summary()`
- `EmbeddingRepository` - Vector embedding operations
  - `create()`, `create_many()`, `get_by_cv()`, `count_by_cv()`
  - `search_similar_in_cv()` - Cosine similarity search
  - `search_similar_all()` - Cross-CV search with user filter
  - `search_by_threshold()` - Distance-based filtering
  - `SimilarityResult` - Data class with distance and similarity scores

**CV Service Rewrite (`cv_service.py`)**
- Complete integration with LangChain and repositories
- `process_and_evaluate()` - Full pipeline:
  1. Validate file (PDF/DOCX)
  2. Process with `DocumentProcessor` (LangChain)
  3. Create CV record in database
  4. Generate and store embeddings (pgvector)
  5. Evaluate with `EvaluationChain` (LangChain)
  6. Store evaluation results
  7. Update CV status to EVALUATED
- `get_cv()` - Get CV with ownership check
- `list_user_cvs()` - Paginated list with evaluations
- `delete_cv()` - Delete with cascade to related data
- `re_evaluate()` - Re-run evaluation with different template
- `convert_to_response()` - Convert to API schema
- `ProcessingResult` - Data class for pipeline results

**CV Controller Updates (`cv_controller.py`)**
- `upload_and_evaluate()` - Updated for authentication and new service
- `list_cvs()` - List user's CVs with pagination
- `get_cv()` - Get single CV details
- `delete_cv()` - Delete CV and related data
- `re_evaluate_cv()` - Re-evaluate with different template
- Authentication required for all CV operations

**CV Routes Updates (`cv_routes.py`)**
- 6 routes with authentication:
  - `POST /api/cv/upload` - Upload and evaluate (auth required)
  - `GET /api/cv/` - List user's CVs (auth required)
  - `GET /api/cv/{cv_id}` - Get CV details (auth required)
  - `DELETE /api/cv/{cv_id}` - Delete CV (auth required)
  - `POST /api/cv/{cv_id}/re-evaluate` - Re-evaluate CV (auth required)
  - `GET /api/cv/health` - Health check (public)

**CV Schemas (`cv_schemas.py`)**
- `CVSummary` - Summary for list views
- `CVListResponse` - Paginated list response
- `CVDetailResponse` - Full CV details with evaluation
- `EvaluationDetail` - Detailed evaluation information

**CV Dependencies (`cv_dependencies.py`)**
- `get_cv_service()` - Now injects database session
- Service has access to all repositories

### Changed
- CV processing now persists to database instead of in-memory
- Embeddings stored in pgvector for semantic search
- Evaluations stored with full criteria results JSON
- All CV operations require authentication

### Technical Details
- Controller-Service-Repository pattern fully implemented
- Async database operations throughout
- Ownership checks on all CV operations
- Cascade deletes for CV → evaluations, embeddings, chat

---

## [0.5.0] - 2026-02-13 🤖 LANGCHAIN INTEGRATION

### Added

**LangChain Module (`app/langchain/`)**
- Complete LangChain integration for AI-powered CV processing
- Support for both Anthropic (Claude) and OpenAI providers
- BYOK (Bring Your Own Key) support for user-provided API keys

**Configuration (`config.py`)**
- `LangChainSettings` - Environment-based configuration
- `get_llm()` - Factory for Claude/OpenAI chat models
- `get_embeddings()` - Factory for OpenAI embeddings
- Temperature and max_tokens configuration

**Document Processing (`document_processor.py`)**
- `DocumentProcessor` - High-level document processing pipeline
- `load_pdf()` / `load_docx()` - LangChain document loaders
- `process_documents()` - RecursiveCharacterTextSplitter integration
- `ProcessedDocument` - Result container with full_text and chunks

**Embeddings (`embeddings.py`)**
- `EmbeddingService` - pgvector storage integration
- `embed_text()` / `embed_texts()` - Low-level embedding functions
- `store_cv_embeddings()` - Store chunks with vectors
- `search_similar()` - Cosine similarity search within a CV
- `search_all_cvs()` - Cross-CV semantic search

**Evaluation Chain (`chains/evaluation_chain.py`)**
- `EvaluationChain` - CV scoring with structured output
- `CVEvaluationResult` - Pydantic model for evaluation results
- `CriterionScore` - Per-criterion score with reasoning
- Dynamic criteria injection from templates
- PydanticOutputParser for validated LLM output

**Conversation Chain (`chains/conversation_chain.py`)**
- `ConversationChain` - RAG-powered Q&A about CVs
- `ExplanationChain` - Detailed score explanations
- `ChatMessage` - Message model for chat history
- Context retrieval from CV embeddings
- Conversation history support

### Dependencies Added
- `langchain>=0.3.0`
- `langchain-core>=0.3.0`
- `langchain-anthropic>=0.3.0`
- `langchain-openai>=0.2.0`
- `langchain-postgres>=0.0.12`
- `langchain-text-splitters>=0.3.0`
- `langchain-community>=0.3.0`
- `docx2txt` (for DOCX loading)

---

## [0.4.0] - 2026-02-13 🗄️ DATABASE LAYER

### Added

**PostgreSQL + pgvector Integration**
- Async SQLAlchemy 2.0 with asyncpg driver
- pgvector extension support for semantic search
- Alembic migrations setup for schema management

**Database Models (10 tables)**
- `User` - User accounts with auth provider tracking, OAuth support
- `UserApiKey` - Encrypted API keys for AI providers (AES-256)
- `UserAgentConfig` - Per-agent AI provider/model configuration
- `EvaluationTemplate` - System and user-created evaluation templates
- `TemplateCriterion` - Individual criteria within templates
- `CV` - Uploaded CV documents with status tracking
- `CVEvaluation` - Evaluation results with per-criterion scores
- `CVEmbedding` - Vector embeddings for semantic search
- `ChatHistory` - Conversation history for CV explanations
- `NotificationSettings` - Email/WhatsApp alert preferences

**User Repository**
- `app/features/auth/auth_repository.py` - Database operations for users
- Async CRUD operations for user management
- Replaced in-memory UserStore with PostgreSQL persistence

**Encryption Utilities**
- `app/db/encryption.py` - AES-256 (Fernet) encryption for API keys
- Key hint extraction (last 4 chars) for UI display
- Encryption key validation

**Seed Data**
- "AI-First Fintech" system template with 5 criteria
- Seed script for initial database population

**Configuration**
- `DATABASE_URL` environment variable
- `ENCRYPTION_KEY` for API key encryption
- Updated `.env.example` with all new variables

**Documentation**
- `docs/POSTGRESQL_SETUP.md` - Installation guide for PostgreSQL/pgvector

### Changed
- **Auth Feature** - Fully refactored to use database persistence
  - `auth_service.py` - Now async, uses UserRepository
  - `auth_controller.py` - Accepts AsyncSession dependency
  - `auth_dependencies.py` - Async user lookup from database
  - `auth_routes.py` - Injects database session
- Config now includes database and encryption settings
- User model centralized in `app/db/models/user.py`

### Removed
- `app/features/auth/auth_models.py` - Obsolete in-memory UserStore

---

## [0.3.0] - 2026-02-12 🏗️ REFACTORING + EXPANDED CRITERIA

### Added

**Expanded Evaluation Criteria (5 total)**
- **Education** (15 pts) - High School+, bootcamps, self-taught
- **Fintech Experience** (20 pts) - Finance, crypto, DeFi
- **Technical Skills** (25 pts) - TypeScript, Python, React, FastAPI
- **Soft Skills & Adaptability** (20 pts) - Fast learner, stress handling, teamwork
- **AI-Native Development** (20 pts) - NEW
  - AI coding tools (Claude Code, Copilot, Cursor, Windsurf)
  - Vibe coding / AI pair programming
  - RAG systems understanding
  - MCP (Model Context Protocol) familiarity
  - AI agent development (LangChain, LlamaIndex)

**Controller-Service-Model Architecture**
- `core/` module with shared infrastructure
  - `security.py` - JWT utils, password hashing
  - `exceptions.py` - Custom exception classes
  - `dependencies.py` - Shared FastAPI dependencies
- `shared/schemas/` for base response schemas
- Feature-based organization with routes/controller/service separation

**Documentation**
- Comprehensive Python docstrings (Google-style) for all modules
- Updated PROJECT_CONTEXT.md with architecture details
- Updated README.md with new criteria

### Changed

**Project Structure Refactoring**
- Moved from `routers/`, `services/`, `models/` to feature-based structure
- Auth module: `auth_routes.py`, `auth_controller.py`, `auth_service.py`, etc.
- CV module: `cv_routes.py`, `cv_controller.py`, `cv_service.py`, etc.
- PDF and evaluation services moved to `cv/services/`

**Pass/Fail Logic Update**
- Now requires 3+ out of 5 criteria (was 2/3)
- Technical Skills is mandatory for pass
- Score threshold remains ≥ 60

### Removed
- Old `routers/cv_router.py`
- Old `services/` directory at root
- Old `models/schemas.py`

---

## [0.2.0] - 2025-02-12 🔐 AUTHENTICATION

### Added

**JWT Authentication System**
- `POST /api/auth/register` - User registration with email/password
- `POST /api/auth/login` - User login with email/password
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/google` - Google OAuth authentication
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/logout` - Logout (client-side token discard)

**User Management**
- In-memory user storage (temporary, database in Phase 2)
- Password hashing with bcrypt (12 rounds)
- JWT access tokens (30 min expiry)
- JWT refresh tokens (7 day expiry)

**Auth Schemas**
- `RegisterRequest` - Email, password, full name
- `LoginRequest` - Email, password
- `AuthResponse` - User + tokens
- `TokenResponse` - Access/refresh tokens
- `UserResponse` - Public user data

**Security Features**
- Bearer token authentication via HTTP header
- Token type validation (access vs refresh)
- Password length truncation for bcrypt (72 byte limit)

### Configuration
- `JWT_SECRET_KEY` - Secret for signing tokens
- `JWT_ALGORITHM` - HS256 by default
- `ACCESS_TOKEN_EXPIRE_MINUTES` - 30 minutes
- `REFRESH_TOKEN_EXPIRE_DAYS` - 7 days
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Optional OAuth

---

## [0.1.0] - 2025-01-XX 🚀 MVP RELEASE

### Added

**Core CV Upload & Evaluation API**
- `POST /api/cv/upload` - Upload PDF CV and receive AI-powered evaluation
- `GET /api/cv/health` - Health check endpoint for API status

**PDF Processing Service**
- PDF text extraction using pdfplumber
- Handles multi-page documents
- Error handling for corrupted or invalid PDFs

**AI Evaluation Service**
- Claude AI integration via Anthropic API
- System prompt with expert CV screener persona
- Evaluates 3 core criteria (expanded to 5 in v0.3.0)
- Returns structured JSON response with scoring and reasoning

**Data Models (Pydantic)**
- `CVEvaluationResponse` - Full evaluation result with criteria breakdown
- `UploadResponse` - Wrapper for upload endpoint response
- `EvaluationCriteria` - Individual criterion details

**Configuration**
- Environment-based settings with pydantic-settings
- Secure API key management via `.env`
- CORS configuration for frontend integration

### Technical Details
- FastAPI framework for high-performance async API
- Modular architecture with services, routers, and models separation
- Feature-based directory structure for scalability

---

## [Unreleased]

### Planned - Phase 2: Database Layer
- PostgreSQL integration with SQLAlchemy
- pgvector for semantic search capabilities
- User, CV, and Evaluation models
- Database migrations with Alembic

### Planned - Phase 3: LangChain Integration
- Document processing chains
- Structured output parsing
- Conversation chains

### Planned - Phase 4: Multi-Agent Architecture
- Parser Agent, Scorer Agent, Notification Agent
