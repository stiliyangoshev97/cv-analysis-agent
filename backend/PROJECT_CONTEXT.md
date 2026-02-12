# 📋 CV Analysis Agent Backend - Project Context

> Quick reference for AI assistants and developers.  
> Last Updated: February 2025 (v0.2.0 - Authentication)

---

## 🎯 Platform Overview

**CV Analysis Agent** is an AI-powered CV screening platform that uses Claude AI to evaluate resumes against customizable criteria. The system extracts text from PDF CVs, sends it to Claude for intelligent analysis, and returns a detailed scorecard with pass/fail recommendations.

---

## 📊 Current Status

| Component | Progress | Notes |
|-----------|----------|-------|
| Project Setup | ✅ 100% | FastAPI + Python 3.13 |
| PDF Processing | ✅ 100% | pdfplumber extraction |
| AI Evaluation | ✅ 100% | Claude API integration |
| CV Upload API | ✅ 100% | Single CV upload + evaluation |
| Health Check | ✅ 100% | Basic health endpoint |
| CORS Config | ✅ 100% | Frontend integration ready |
| Environment Config | ✅ 100% | pydantic-settings |
| **Authentication** | ✅ 100% | JWT + Email/Password + Google OAuth ready |
| **Database Layer** | ⏳ 0% | Phase 2 - PostgreSQL + pgvector |
| **LangChain Integration** | ⏳ 0% | Phase 3 |
| **Multi-Agent System** | ⏳ 0% | Phase 4 |
| **Notification System** | ⏳ 0% | Phase 5 - Email + WhatsApp |

**Overall Progress: ~30%** (MVP + Auth Complete)

---

## 🏗️ Architecture

### Tech Stack
| Layer | Technology | Purpose |
|-------|------------|---------|
| Runtime | Python 3.13 | Server runtime |
| Framework | FastAPI | Async HTTP server & routing |
| PDF Processing | pdfplumber | Text extraction from PDFs |
| AI | Anthropic Claude | CV evaluation & reasoning |
| Validation | Pydantic | Schema validation & serialization |
| Config | pydantic-settings | Environment management |

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Settings with pydantic-settings
│   ├── main.py                # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── cv_router.py       # CV upload endpoints
│   └── services/
│       ├── __init__.py
│       ├── pdf_service.py     # PDF text extraction
│       └── evaluation_service.py  # Claude AI integration
├── requirements.txt
├── .env                       # API keys (gitignored)
├── .env.example              # Template for environment vars
├── README.md
├── CHANGELOG.md
└── PROJECT_CONTEXT.md
```

---

## 🔌 API Endpoints

### Current Endpoints (v0.1.0)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/cv/upload` | Upload PDF CV for evaluation | None |
| `GET` | `/api/cv/health` | Health check | None |

### Upload Response Schema
```json
{
  "status": "success",
  "data": {
    "candidate_name": "John Doe",
    "overall_score": 75,
    "pass_fail": "pass",
    "criteria": [
      {
        "name": "Education Background",
        "score": 15,
        "max_score": 20,
        "met": true,
        "reasoning": "..."
      }
    ],
    "overall_reasoning": "...",
    "recommendation": "..."
  }
}
```

---

## 📝 Evaluation Criteria

| Criterion | Max Score | Weight | Description |
|-----------|-----------|--------|-------------|
| Education Background | 20 | 20% | Degree level and relevance |
| Fintech Experience | 40 | 40% | Years and quality of industry experience |
| Technical Skills | 40 | 40% | Programming languages, frameworks, tools |

### Scoring Thresholds
- **Pass**: ≥ 60 points
- **Fail**: < 60 points

---

## 🛠️ Development

### Running the Server
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Environment Variables
```env
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 📋 Planned Features (Roadmap)

### Phase 1: Authentication
- [ ] JWT authentication with python-jose
- [ ] Email/password registration
- [ ] Google OAuth
- [ ] Password hashing (bcrypt)

### Phase 2: Database Layer
- [ ] PostgreSQL with SQLAlchemy
- [ ] pgvector for embeddings
- [ ] User model
- [ ] CV model (store uploads)
- [ ] Evaluation model (store results)
- [ ] Alembic migrations

### Phase 3: LangChain Integration
- [ ] LangChain orchestration
- [ ] Structured output chains
- [ ] Prompt templates
- [ ] Memory for chat context

### Phase 4: Multi-Agent System
- [ ] Parser Agent
- [ ] Scorer Agent
- [ ] Notification Agent
- [ ] Chat Agent

### Phase 5: Notification System
- [ ] Email notifications (SendGrid/Resend)
- [ ] WhatsApp notifications (Twilio)
- [ ] User notification preferences

### Phase 6: Signature Features
- [ ] Candidate Match-Up (compare 2 CVs)
- [ ] Explainable Scoring (detailed breakdowns)
- [ ] High-Flyer Alerts (exceptional candidates)
- [ ] Adaptive Personas (different evaluator styles)
- [ ] Semantic Search (search across all CVs)

---

## 🔒 Security Considerations

- API keys stored in `.env` (gitignored)
- CORS configured for specific frontend origin
- File type validation (PDF only)
- File size limits to be implemented
- Rate limiting planned for production

---

## 📚 Related Documentation

- [Main README](/README.md) - Project overview
- [TODO.md](/TODO.md) - Detailed 8-phase roadmap
- [CV-Scanner.md](/CV-Scanner.md) - Feature elevation plan
- [Frontend PROJECT_CONTEXT](/frontend/PROJECT_CONTEXT.md) - Frontend documentation
