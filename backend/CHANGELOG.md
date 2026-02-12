# Changelog

All notable changes to the CV Analysis Agent backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Evaluates 3 core criteria:
  - **Education Background** (20 points) - Degree level and field
  - **Fintech Experience** (40 points) - Industry experience and roles
  - **Technical Skills** (40 points) - Programming languages and technologies
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

### Planned - Phase 1: Authentication
- JWT-based authentication with python-jose
- Email/password registration and login
- Google OAuth integration
- Password hashing with bcrypt

### Planned - Phase 2: Database Layer
- PostgreSQL integration with SQLAlchemy
- pgvector for semantic search capabilities
- User, CV, and Evaluation models
- Database migrations with Alembic

### Planned - Phase 3: Multi-Agent Architecture
- LangChain orchestration
- Parser Agent - CV text extraction and structuring
- Scorer Agent - Intelligent evaluation
- Notification Agent - Email/WhatsApp alerts
- Chat Agent - Interactive Q&A about CVs
