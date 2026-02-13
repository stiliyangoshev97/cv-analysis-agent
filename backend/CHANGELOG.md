# Changelog

All notable changes to the CV Analysis Agent backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] - 2026-02-13 🗄️ DATABASE LAYER

### Added

**PostgreSQL + pgvector Integration**
- Async SQLAlchemy 2.0 with asyncpg driver
- pgvector extension support for semantic search
- Alembic migrations setup for schema management

**Database Models (10 tables)**
- `User` - User accounts with auth provider tracking
- `UserApiKey` - Encrypted API keys for AI providers (AES-256)
- `UserAgentConfig` - Per-agent AI provider/model configuration
- `EvaluationTemplate` - System and user-created evaluation templates
- `TemplateCriterion` - Individual criteria within templates
- `CV` - Uploaded CV documents with status tracking
- `CVEvaluation` - Evaluation results with per-criterion scores
- `CVEmbedding` - Vector embeddings for semantic search
- `ChatHistory` - Conversation history for CV explanations
- `NotificationSettings` - Email/WhatsApp alert preferences

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
- Config now includes database and encryption settings
- Models prepared for migration from in-memory to PostgreSQL

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
