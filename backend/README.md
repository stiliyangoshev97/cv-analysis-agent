# CV Screening Agent - Backend 🐍

FastAPI backend for AI-powered CV screening. Extracts text from PDF resumes and evaluates them using Claude AI against 5 modern hiring criteria.

## 🎯 Features

- **PDF Processing**: Extract text from uploaded PDF resumes using pdfplumber
- **AI Evaluation**: Claude AI scores CVs against 5 criteria with detailed reasoning
- **JWT Authentication**: Secure user registration, login, and token refresh
- **Google OAuth**: Optional Google sign-in support
- **RESTful API**: Clean, documented endpoints with OpenAPI/Swagger

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

## 🏗️ Architecture

### Controller-Service-Model Pattern
```
Request → Routes → Controller → Service → External APIs/Models
              ↓          ↓           ↓
           Thin     HTTP Logic   Business Logic
```

### Project Structure
```
backend/app/
├── main.py                     # FastAPI entry point
├── config.py                   # Environment settings
├── core/                       # Shared infrastructure
│   ├── security.py             # JWT utils, password hashing
│   ├── exceptions.py           # Custom exception classes
│   └── dependencies.py         # Shared FastAPI dependencies
├── shared/schemas/             # Base response schemas
│   └── base.py                 # BaseResponse, ErrorResponse
└── features/
    ├── auth/                   # Authentication module
    │   ├── auth_routes.py      # Route definitions
    │   ├── auth_controller.py  # HTTP handlers
    │   ├── auth_service.py     # Business logic
    │   ├── auth_schemas.py     # Pydantic schemas
    │   ├── auth_models.py      # User model (in-memory)
    │   └── auth_dependencies.py # get_current_user
    └── cv/                     # CV screening module
        ├── cv_routes.py        # Route definitions
        ├── cv_controller.py    # HTTP handlers
        ├── cv_service.py       # Orchestration
        ├── cv_schemas.py       # Pydantic schemas
        └── services/
            ├── pdf_service.py        # PDF extraction
            └── evaluation_service.py # Claude AI evaluation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API key

### Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Run development server
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
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/auth/register` | Register new user | ❌ |
| `POST` | `/api/auth/login` | Login with email/password | ❌ |
| `POST` | `/api/auth/refresh` | Refresh access token | ❌ |
| `POST` | `/api/auth/google` | Google OAuth exchange | ❌ |
| `GET` | `/api/auth/me` | Get current user | ✅ |

### CV Screening
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/cv/upload` | Upload PDF & evaluate | ❌ |
| `GET` | `/api/cv/health` | Health check | ❌ |

### Response Schemas

#### Upload Response
```json
{
  "success": true,
  "message": "CV evaluated successfully",
  "evaluation": {
    "status": "pass",
    "match_score": 78,
    "reasoning": "Strong candidate with...",
    "criteria": [
      {
        "name": "Education",
        "passed": true,
        "details": "Bachelor's in Computer Science"
      },
      {
        "name": "Technical Skills",
        "passed": true,
        "details": "Python, TypeScript, React experience"
      }
    ],
    "candidate_name": "John Doe"
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_cv_service.py
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🛣️ Roadmap

- [x] PDF text extraction
- [x] Claude AI evaluation
- [x] JWT authentication
- [x] Controller-Service-Model refactor
- [ ] PostgreSQL database
- [ ] pgvector for embeddings
- [ ] LangChain integration
- [ ] Multi-agent architecture
