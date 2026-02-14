# Changelog

All notable changes to the CV Analysis Agent backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.14.3] - 2026-02-15 👤 CANDIDATE NAME EXTRACTION

### Fixed

**CV Service (`cv_service.py`)**
- Now extracts candidate name from CV text during upload processing
- Uses `extract_candidate_name()` function from `agents/tools.py`
- Candidate name is stored in the CV record and returned in API responses
- Fixed "Unknown Candidate" issue in history and comparison views

### Changed

**CV Service**
- Added import for `extract_candidate_name` from `app.agents.tools`
- Candidate name extraction happens after document processing (Step 2.5)
- `convert_to_response()` now returns actual candidate name instead of `None`

---

## [0.14.2] - 2026-02-15 🔑 USER API KEYS INTEGRATION

### Added

**User Keys Service (`settings/user_keys_service.py`)**
- `UserAPIKeys` dataclass - Container for user's decrypted API keys
- `UserKeysService` class - Fetches and validates user keys for CV/Chat operations
- `validate_keys_for_cv_processing()` - Ensures required keys are configured

### Changed

**CV Service (`cv_service.py`)**
- Now fetches user's API keys before processing
- Creates `EmbeddingService` with user's OpenAI key
- Creates `EvaluationChain` with user's preferred LLM provider/key
- `re_evaluate()` also uses user keys (per-request LLM instantiation)
- Removed fallback to environment variables - users MUST configure keys

**Chat Service (`chat_service.py`)**
- `ask()` now uses user's LLM key for responses
- `explain_criterion()` uses user's LLM key
- `compare_cvs()` uses user's LLM key
- LangChain components created per-request with user keys

**Embedding Service (`langchain/embeddings.py`)**
- Added `api_key` parameter to `__init__()`
- Supports BYOK (Bring Your Own Key) for embeddings

**main.py**
- Removed Anthropic API key check from startup
- Updated startup message to reflect user key management

**config.py**
- Commented out legacy `anthropic_api_key` setting
- Added documentation that keys come from user settings

**Tests Updated**
- `test_cv_service.py` - Updated all tests to mock `UserKeysService` and per-request LLM creation
- `test_chat_service.py` - Updated tests for user keys architecture
- `conftest.py` - Removed deprecated `anthropic_api_key` from test settings
- `conftest.py` - Added `test_user_api_keys` fixture for integration tests
- `test_chat_api.py` - Fixed integration tests for user keys architecture (mock paths, return types)

### Security

- **No system API keys**: All AI operations use user-provided keys
- Keys are encrypted in database (AES-256)
- No fallback to `.env` - forces proper user setup

### Fixed

- `user_keys_service.py` - Fixed `get_user_keys()` to use `scorer_provider` instead of non-existent `default_llm_provider`
- Integration tests - Fixed compare_cvs mocks to return dict (matching controller expectations)

---

## [0.14.1] - 2026-02-14 🔒 FILE TYPE VALIDATION SECURITY

### Added

**File Type Security (`cv_controller.py`)**
- `ALLOWED_EXTENSIONS` constant - Whitelist: `.pdf`, `.docx`, `.doc`
- `ALLOWED_MIME_TYPES` constant - Valid MIME types for CVs
- `BLOCKED_EXTENSIONS` constant - Blocklist of dangerous file types
- `_validate_file_magic()` method - Magic byte validation for file authenticity

**Magic Byte Validation**
- PDF files must start with `%PDF-`
- DOCX files must be valid ZIP archives (`PK\x03\x04`)
- DOC files must be OLE compound documents (`\xD0\xCF\x11\xE0`)

### Changed

**CV Upload Validation**
- Enhanced `_validate_upload()` with 4-layer security:
  1. Extension whitelist check
  2. Blocked extension check (images, executables, scripts, archives)
  3. MIME type validation (blocks `image/*`, `video/*`, `audio/*`, `text/html`)
  4. Magic byte verification

### Security

- **Defense in depth**: Multiple validation layers prevent malicious uploads
- Blocks: `.exe`, `.bat`, `.sh`, `.js`, `.py`, `.php`, `.html`, `.zip`, `.tar`, images, media
- Prevents file extension spoofing with magic byte verification
- Works with frontend validation for comprehensive security

---

## [0.14.0] - 2026-02-14 ⚙️ USER SETTINGS API

### Added

**Settings Feature (`app/features/settings/`)** - Complete user configuration module
- `settings_schemas.py` - Pydantic schemas for API keys and agent config
- `settings_repository.py` - Database CRUD for UserApiKey and UserAgentConfig
- `settings_service.py` - Business logic with key validation
- `settings_controller.py` - HTTP handlers
- `settings_routes.py` - 8 REST endpoints with rate limiting

**API Key Management**
- Store encrypted API keys for OpenAI, Anthropic, and Gemini
- Validate keys by making test API calls before storing
- Display key hints (last 4 chars) for identification
- AES-256 encryption for secure storage

**LLM Provider Configuration**
- Users can choose default LLM provider (Claude, GPT, or Gemini)
- Per-agent overrides (chat vs evaluation)
- Model selection per provider
- Embeddings always use OpenAI (enforced, not user-configurable)

**New API Endpoints (`/api/settings`)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api-keys` | List API keys (hints only) |
| `PUT` | `/api-keys/{provider}` | Set/update API key |
| `DELETE` | `/api-keys/{provider}` | Delete API key |
| `POST` | `/validate-key` | Validate key without storing |
| `GET` | `/agent-config` | Get LLM preferences |
| `PUT` | `/agent-config` | Update LLM preferences |
| `GET` | `/available-models` | List available models |
| `GET` | `/setup-status` | Check setup completion |

**Available Models Endpoint**
- Returns all supported LLM providers and their models
- Anthropic: Claude Sonnet 4, Claude 3.5 Sonnet, Claude 3 Opus
- OpenAI: GPT-4o, GPT-4 Turbo, GPT-4
- Gemini: Gemini 1.5 Flash, Gemini 1.5 Pro, Gemini 2.0 Flash

### Changed

**Dependencies Updated**
- Added `openai>=1.0.0` - Direct SDK for key validation
- Added `google-genai>=1.0.0` - Direct SDK for Gemini key validation (new package, replaces deprecated `google-generativeai`)
- Added `docx2txt>=0.8` - DOCX document processing
- Reorganized `requirements.txt` with clear sections

**Unit Tests**
- Added `test_settings_service.py` with 29 tests covering:
  - API Key CRUD and validation (OpenAI, Anthropic, Gemini)
  - Agent Config get/update
  - Setup status checks
  - Available models listing

**Documentation**
- Updated `.env.example` with clearer BYOK instructions
- Updated `TODO.md` with frontend settings tasks
- Updated `main.py` with settings router and v0.14.0 version

### Architecture

```
BYOK (Bring Your Own Key) Flow:
┌─────────────────┐    ┌────────────────┐    ┌─────────────────┐
│ Frontend        │───▶│ /api/settings  │───▶│ Encrypted DB    │
│ Settings Page   │    │ API            │    │ Storage         │
└─────────────────┘    └────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              API Key Validation   Agent Config
              (test API calls)     (LLM preferences)

Required Setup:
  1. User configures OpenAI key (for embeddings) ← REQUIRED
  2. User configures LLM key (Claude/GPT/Gemini) ← AT LEAST ONE
  3. User selects preferred LLM provider
  4. User can now upload CVs
```

### Notes
- **OpenAI API key is MANDATORY** for CV uploads (embeddings)
- **LLM provider is user's choice** - configure one or more
- Keys are validated before storage with actual API calls
- Frontend must check `/api/settings/setup-status` before allowing uploads

---

## [0.13.0] - 2026-02-14 🤖 GEMINI LLM SUPPORT

### Added

**Google Gemini Provider (`app/langchain/config.py`)**
- Added `gemini` as third LLM provider option alongside `anthropic` and `openai`
- Supports Gemini 1.5 Flash (default) and Gemini 1.5 Pro models
- Graceful fallback if `langchain-google-genai` package not installed
- Full BYOK (Bring Your Own Key) support for Google API keys

**Configuration Settings**
- `GOOGLE_API_KEY` - Google AI Studio API key
- `GEMINI_MODEL` - Model selection (default: `gemini-1.5-flash`)
- `DEFAULT_LLM_PROVIDER` now accepts `"gemini"` as valid option

**AI Provider Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    AI Provider Architecture                  │
├─────────────────────────────────────────────────────────────┤
│  EMBEDDINGS (Required)          LLM (User Choice)           │
│  ┌─────────────────┐           ┌─────────────────┐         │
│  │  OpenAI Only    │           │  Claude (Anthropic) │     │
│  │  (mandatory for │           │  GPT (OpenAI)        │     │
│  │   pgvector)     │           │  Gemini (Google)     │     │
│  └─────────────────┘           └─────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Changed

**Documentation Updates**
- `.env.example` - Added Gemini configuration with organized AI section
- `README.md` - Updated tech stack and added AI Provider Architecture diagram

### Dependencies Added
- `langchain-google-genai>=2.0.0` - Google Gemini support for LangChain

### Notes
- **Embeddings remain OpenAI-only** - Required for pgvector vector consistency across all CVs
- **LLM is user choice** - Users can select Claude, GPT, or Gemini for evaluation and chat
- Gemini integration follows same BYOK pattern as other providers

---

## [0.12.0] - 2026-02-14 🛡️ RATE LIMITING

### Added

**Rate Limiting Infrastructure (`app/core/rate_limit.py`)**
- `slowapi` integration for request rate limiting
- Tiered rate limits by endpoint type and authentication status
- User-based rate limiting (by JWT user ID) for authenticated endpoints
- IP-based rate limiting for unauthenticated endpoints

**Rate Limit Tiers**

| Endpoint Type | Limit | Scope | Rationale |
|--------------|-------|-------|-----------|
| Auth (login, register) | 5/min | Per IP | Prevent brute force |
| CV Upload | 100/hour | Per User | BYOK users pay own costs |
| Chat/RAG | 30/min | Per User | LLM API costs |
| General API | 100/min | Per User | Fair usage |
| Test Notifications | 5/hour | Per User | Prevent spam |
| Public (health) | 60/min | Per IP | Standard |

**Rate Limit Key Functions**
- `get_user_identifier()` - Extract user ID from JWT for rate limiting
- `get_ip_address()` - Fallback to IP for unauthenticated requests
- `rate_limit_exceeded_handler()` - Custom 429 error response

### Changed

**Routes Updated with Rate Limiting**
- Auth routes: `/api/auth/*` (register, login, refresh, google, me, logout)
- CV routes: `/api/cv/*` (upload, list, get, delete, re-evaluate, similarity)
- Chat routes: `/api/chat/*` (ask, history, explain, compare)
- Notification routes: `/api/notifications/*` (settings, test, status)
- Profile routes: `/api/profiles/*` (CRUD, criteria)

**Profile Routes Refactored**
- Changed from `router.add_api_route()` to decorator syntax
- Enables proper rate limiting decorator application

### Dependencies Added
- `slowapi>=0.1.9` - Rate limiting for FastAPI

---

## [0.11.0] - 2026-02-14 🧪 BACKEND TESTING (Phase 8.1)

### Added

**Testing Infrastructure**
- `pytest.ini` - Pytest configuration with markers and asyncio settings
- `requirements-test.txt` - Test dependencies (pytest-asyncio, pytest-mock, httpx, faker, etc.)
- `app/tests/conftest.py` - Comprehensive shared fixtures:
  - SQLite in-memory database for fast tests
  - Async test client with OpenAI embeddings mock
  - User, CV, template, evaluation fixtures
  - Auth token helpers

**Unit Tests (`app/tests/unit/`)** - 169 tests
- `test_auth.py` - 21 tests for AuthService:
  - Password hashing (bcrypt verification)
  - JWT token creation/validation
  - User registration with duplicate detection
  - Login with password verification
  - Token refresh flow
- `test_profile_service.py` - 28 tests for ProfileService:
  - Profile CRUD operations
  - Authorization checks (system vs user templates)
  - Profile cloning logic
  - Criterion management
- `test_similarity_service.py` - 26 tests for SimilarityService:
  - Cosine similarity calculations
  - Average embedding computation
  - CV ranking algorithms
  - Similar CV search logic
  - Comparison matrix generation
- `test_cv_service.py` - 32 tests for CVService:
  - Process and evaluate pipeline
  - CV retrieval with ownership checks
  - Paginated CV listing
  - CV deletion with cascading
  - Re-evaluation with different templates
  - Schema conversion helpers
  - Service health checks
- `test_chat_service.py` - 28 tests for ChatService:
  - CV ownership verification
  - RAG Q&A pipeline (ask)
  - Chat history retrieval and clearing
  - Criterion explanation
  - Multi-CV comparison (2-5 CVs)
- `test_notification_service.py` - 34 tests for NotificationService:
  - NotificationDispatchResult dataclass
  - Get/update notification settings
  - Threshold checking
  - Full dispatch pipeline (email + WhatsApp)
  - Test notification sending

**Integration Tests (`app/tests/integration/`)** - 114 tests
- `test_auth_api.py` - 14 tests for `/api/auth/*`:
  - Register, login, me, refresh endpoints
  - Validation errors, duplicate detection
  - JWT token flows
- `test_profile_api.py` - 25 tests for `/api/profiles/*`:
  - Profile CRUD endpoints
  - Criterion management endpoints
  - Clone functionality
  - Authorization (system template protection)
- `test_cv_api.py` - 18 tests for `/api/cv/*`:
  - List, get, delete CV endpoints
  - Similar CVs, ranking, comparison endpoints
  - Semantic search endpoint
- `test_chat_api.py` - 28 tests for `/api/chat/*`:
  - Ask question about CV (RAG)
  - Get/clear chat history
  - Explain criterion score
  - Compare multiple CVs (2-5)
  - Authorization and validation
- `test_notification_api.py` - 29 tests for `/api/notifications/*`:
  - Get notification settings (with masked WhatsApp)
  - Update notification settings (email, WhatsApp, threshold)
  - Send test notifications (email, WhatsApp channels)
  - Get service configuration status
  - Validation (phone format, threshold bounds)
  - Edge cases (concurrent updates, boundary values)

### Fixed

**Bug Fixes Discovered During Testing**
- `ProfileService.update_profile()` - Fixed: Reload template with criteria after update
- `cv_routes.py` - Fixed: Return type hints (removed `-> dict` where Pydantic models returned)
- `chat_service.py` - Fixed: Use `score` instead of `total_score` (model attribute name)
- `chat_service.py` - Fixed: Handle both dict and list formats for `criteria_results`
- `chat_routes.py` - Fixed: Route ordering (`/compare` before `/{cv_id}`)

### Changed

**Test Configuration**
- Mocked OpenAI embeddings in conftest to avoid requiring API key
- Session-scoped database engine for test isolation
- Async test support with `pytest-asyncio`

### Bug Fixes (Resolved)

| Issue | Fix | Location |
|-------|-----|----------|
| `CVEmbedding.chunk_index` missing | Added `chunk_text` and `chunk_index` columns | `cv.py`, migration |
| pgvector unavailable in SQLite | Mock `SimilarityService` methods | `test_cv_api.py` |
| SQLAlchemy session caching | Verify delete via 404 on retry | `test_profile_api.py` |

### Test Summary

```
Total: 283 passed, 0 skipped
├── Unit Tests: 169 passed
│   ├── test_auth.py: 21 tests
│   ├── test_profile_service.py: 28 tests
│   ├── test_similarity_service.py: 26 tests
│   ├── test_cv_service.py: 32 tests
│   ├── test_chat_service.py: 28 tests
│   └── test_notification_service.py: 34 tests
└── Integration Tests: 114 passed
    ├── test_auth_api.py: 14 tests
    ├── test_profile_api.py: 25 tests
    ├── test_cv_api.py: 18 tests
    ├── test_chat_api.py: 28 tests
    └── test_notification_api.py: 29 tests
```

---

## [0.10.0] - 2026-02-14 📋 HIRING PROFILES + VECTOR SIMILARITY (Phase 6)

### Added

**Hiring Profile Feature (`app/features/profile/`)** - Complete profile management module
- `profile_schemas.py` - Pydantic schemas with Google-style docstrings:
  - `CriterionCreate`, `CriterionUpdate`, `CriterionResponse` - Criterion CRUD
  - `ProfileCreate`, `ProfileUpdate`, `ProfileResponse`, `ProfileSummary` - Profile CRUD
  - `ProfileListResponse`, `CloneProfileRequest` - List and clone operations
- `profile_service.py` - Business logic with authorization:
  - `ProfileService` class wrapping `TemplateRepository`
  - Authorization: system templates read-only, user templates private
  - Profile CRUD: list, get, create, update, delete, clone
  - Criterion CRUD: add, update, delete criteria within profiles
- `profile_controller.py` - HTTP handlers with error handling:
  - `ProfileController` class with static methods
  - Proper HTTP status codes (201 for create, 404 for not found, 403 for forbidden)
- `profile_routes.py` - 9 REST endpoints with OpenAPI descriptions
- `__init__.py` - Module exports with comprehensive docstrings

**Vector Similarity Search (`app/features/cv/similarity_service.py`)** - CV matching
- `SimilarityService` class for vector-based CV search:
  - `find_similar_cvs()` - Find CVs similar to a given CV
  - `get_cv_ranking()` - Get percentile ranking among all CVs
  - `compare_cvs()` - Head-to-head comparison with similarity matrix
  - `search_by_query()` - Natural language semantic search
- Dataclasses: `SimilarCVResult`, `CVRankingResult`, `CVComparisonResult`
- Uses pgvector cosine similarity for embedding search

**New API Endpoints**

**Profiles (`/api/profiles`):**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all profiles (system + user) |
| `GET` | `/{id}` | Get profile with criteria |
| `POST` | `/` | Create new profile |
| `PUT` | `/{id}` | Update profile metadata |
| `DELETE` | `/{id}` | Delete user profile |
| `POST` | `/{id}/clone` | Clone profile (system or own) |
| `POST` | `/{id}/criteria` | Add criterion to profile |
| `PUT` | `/{id}/criteria/{cid}` | Update criterion |
| `DELETE` | `/{id}/criteria/{cid}` | Delete criterion |

**Similarity (`/api/cv`):**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/{id}/similar` | Find similar CVs |
| `GET` | `/{id}/ranking` | Get percentile ranking |
| `POST` | `/compare` | Compare multiple CVs |
| `POST` | `/search` | Semantic search by query |

**Updated Files:**
- `cv_schemas.py` - Added similarity response schemas
- `cv_controller.py` - Added similarity handler methods
- `cv_routes.py` - Added 4 similarity endpoints
- `cv_dependencies.py` - Added `get_similarity_service`
- `cv/__init__.py` - Export new service and schemas

**OpenAPI Documentation (`app/main.py`)**
- Updated API description to reflect current features
- Bumped version to 0.10.0
- Added feature overview table with all API modules

### Architecture

```
Similarity Search:
┌─────────────────┐    ┌───────────────────┐    ┌────────────────────┐
│ cv_routes.py    │───▶│ cv_controller.py  │───▶│ similarity_service │
│ (4 endpoints)   │    │ (HTTP handlers)   │    │ (vector search)    │
└─────────────────┘    └───────────────────┘    └────────────────────┘
                                                          │
                              ┌────────────────────────────┼────────────────┐
                              ▼                            ▼                ▼
                       EmbeddingRepository          CVRepository    EvaluationRepository
                       (pgvector search)            (CV data)       (scores)
```

### Technical Details
- Reuses existing `TemplateRepository` from cv feature for profiles
- Vector similarity uses averaged chunk embeddings per CV
- Cosine similarity for all comparisons
- Percentile ranking based on evaluation scores
- Google-style docstrings throughout with examples

---

## [0.9.0] - 2026-02-13 🔔 NOTIFICATION SYSTEM (Phase 5)

### Added

**Notification Feature (`app/features/notification/`)** - Complete notification module
- `notification_schemas.py` - Pydantic schemas:
  - `NotificationSettingsResponse`, `NotificationSettingsUpdate`
  - `SendTestNotificationRequest`, `NotificationResultResponse`
  - `CVNotificationData` - Internal data for CV notifications
- `notification_repository.py` - Database CRUD for `NotificationSettings`
  - `get_by_user_id()`, `create()`, `update()`, `get_or_create()`
- `email_service.py` - Async email service
  - `EmailService` class with `aiosmtplib` for async SMTP
  - HTML email templates for CV evaluation notifications
  - `send_cv_notification()`, `send_test_email()`
- `whatsapp_service.py` - WhatsApp via Twilio
  - `WhatsAppService` class using Twilio SDK
  - Formatted WhatsApp messages for CV notifications
  - `send_cv_notification()`, `send_test_message()`
- `notification_service.py` - Orchestration service
  - `NotificationService` - Coordinates email and WhatsApp dispatch
  - `NotificationDispatchResult` dataclass for tracking results
  - `dispatch_cv_notification()`, `send_test_notification()`
  - Respects user preferences (enabled channels, threshold score)
- `notification_controller.py` - HTTP handlers
- `notification_dependencies.py` - FastAPI DI
- `notification_routes.py` - 4 REST endpoints

**NotificationAgent (`app/agents/notification_agent.py`)** - Full implementation
- Replaced stub with complete implementation
- Task handlers:
  - `CHECK_THRESHOLD` - Check if score meets notification threshold
  - `SEND_EMAIL` - Send email notification for CV
  - `SEND_WHATSAPP` - Send WhatsApp notification for CV
  - `DISPATCH_NOTIFICATION` - Dispatch based on user preferences
- Integrates with `NotificationService`

**New API Endpoints (`/api/notifications`)**
- `GET /api/notifications/` - Get notification settings
- `PUT /api/notifications/` - Update notification settings
- `POST /api/notifications/test/{channel}` - Send test notification (email/whatsapp)
- `GET /api/notifications/status` - Get service configuration status

**Configuration (`app/config.py`)**
- SMTP settings: `smtp_host`, `smtp_port`, `smtp_username`, `smtp_password`, `smtp_from_email`, `smtp_from_name`, `smtp_use_tls`
- Twilio settings: `twilio_account_sid`, `twilio_auth_token`, `twilio_whatsapp_from`

**Dependencies (`requirements.txt`)**
- `aiosmtplib>=3.0.0` - Async SMTP for emails
- `twilio>=9.0.0` - WhatsApp via Twilio API

### Architecture

```
NotificationService
       │
┌──────┴──────┐
▼             ▼
EmailService  WhatsAppService
(aiosmtplib)     (Twilio)

CV Workflow Integration:
  EVALUATE_CV → CHECK_THRESHOLD → DISPATCH_NOTIFICATION
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                         SEND_EMAIL         SEND_WHATSAPP
```

### Technical Details
- Async email sending with `aiosmtplib`
- Twilio SDK runs sync in executor for async compatibility
- User-configurable notification preferences per channel
- Threshold-based notifications (only notify if score >= threshold)
- HTML email templates with professional styling
- Graceful degradation when services not configured

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
