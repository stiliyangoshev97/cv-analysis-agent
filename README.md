# CV Analysis Agent 🤖📄

An AI-powered CV screening platform that evaluates resumes against customizable criteria using frontier AI models. Features a multi-agent architecture, RAG-powered chat, and semantic search capabilities.

**Version:** 0.18.0 | **Last Updated:** February 20, 2026 | **Status:** 🚀 **Live in Production**

## 🌐 Live Demo

| Environment | URL |
|-------------|-----|
| **Frontend** | [cv-analysis-agent.vercel.app](https://cv-analysis-agent.vercel.app) |
| **Backend API** | [cv-analysis-agent.onrender.com](https://cv-analysis-agent.onrender.com) |
| **API Docs** | [cv-analysis-agent.onrender.com/docs](https://cv-analysis-agent.onrender.com/docs) |

## ✨ Highlights

- **BYOK (Bring Your Own Keys)** - No API keys stored in code; users provide their own
- **Multi-LLM Support** - Choose Anthropic Claude, OpenAI GPT, or Google Gemini
- **Custom Evaluation Templates** - Create criteria tailored to any role
- **Semantic Search** - Find similar candidates using AI embeddings
- **RAG Chat** - Ask questions about CVs with context-aware responses
- **Batch Upload** - Evaluate up to 10 CVs simultaneously
- **Beautiful UI** - Modern React frontend with dark mode

## ℹ️ Production Notes

| Feature | Status | Notes |
|---------|--------|-------|
| **CV Upload & Evaluation** | ✅ Works | Full AI evaluation with Claude/GPT/Gemini |
| **WhatsApp Notifications** | ✅ Works | Via Twilio API (BYOK) |
| **Email Notifications** | ⚠️ Local only | Render free tier blocks SMTP ports (25/465/587). Works locally. Production apps typically use email APIs (SendGrid, Resend, etc.) |
| **Google OAuth** | ✅ Works | Full authentication flow |
| **Semantic Search** | ✅ Works | pgvector-powered similarity |

## 🔒 Security

This project uses a **Bring Your Own Keys (BYOK)** model:

- ✅ **No API keys in source code** - Users provide keys via Settings UI
- ✅ **Encrypted storage** - API keys encrypted with AES-256 before database storage
- ✅ **Environment variables** - All secrets loaded from `.env` (gitignored)
- ✅ **JWT authentication** - Secure session management
- ✅ **No hardcoded credentials** - All examples use placeholders (`sk-ant-...`)

### Before Going Public
Ensure your `.env` file is **not** committed (it's in `.gitignore`):
```bash
# Verify .env is ignored
git status --ignored | grep .env
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ with pip
- Node.js 18+ with npm


### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt


# Start the server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Open the App
| URL | Description |
|-----|-------------|
| http://localhost:5173 | Frontend UI |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger API Docs |

## 🏗️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.13** | Runtime |
| **FastAPI** | Async REST API framework |
| **LangChain** | AI chains, prompts, RAG |
| **Multi-LLM** | Claude, GPT-5, Gemini (user choice) |
| **OpenAI Embeddings** | Semantic vectors for RAG |
| **PostgreSQL + pgvector** | Database with vector search |
| **SQLAlchemy 2.0** | Async ORM |
| **Pydantic** | Data validation & schemas |
| **python-jose** | JWT authentication |
| **bcrypt** | Password hashing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | UI library |
| **TypeScript** | Type safety |
| **Vite** | Build tool & dev server |
| **Tailwind CSS** | Utility-first styling |
| **TanStack Query** | Server state management |
| **Zustand** | Client state (auth) |
| **Axios** | HTTP client |
| **CVA** | Variant-based components |
| **Zod** | Schema validation |

## 📁 Project Structure

```
CV Analysis Agent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Environment settings
│   │   ├── core/                   # Shared infrastructure
│   │   │   ├── security.py         # JWT & password utils
│   │   │   ├── exceptions.py       # Custom exceptions
│   │   │   └── dependencies.py     # Shared dependencies
│   │   ├── shared/schemas/         # Base response schemas
│   │   └── features/
│   │       ├── auth/               # Authentication module
│   │       │   ├── auth_routes.py
│   │       │   ├── auth_controller.py
│   │       │   ├── auth_service.py
│   │       │   └── auth_schemas.py
│   │       └── cv/                 # CV screening module
│   │           ├── cv_routes.py
│   │           ├── cv_controller.py
│   │           ├── cv_service.py
│   │           └── services/
│   │               ├── pdf_service.py
│   │               └── evaluation_service.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── providers/              # React Query provider
│   │   ├── router/                 # Routing & guards
│   │   ├── shared/
│   │   │   ├── api/                # Axios client
│   │   │   ├── components/ui/      # Button, Card, Badge, etc.
│   │   │   ├── schemas/            # Zod validation schemas
│   │   │   ├── types/              # TypeScript types
│   │   │   └── utils/              # cn() utility
│   │   └── features/
│   │       ├── auth/               # Login, Register, UserMenu
│   │       └── cv/                 # Upload, Scorecard
│   └── package.json
│
├── TODO.md                         # Development roadmap
└── README.md                       # This file
```

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login with email/password |
| `POST` | `/api/auth/refresh` | Refresh access token |
| `POST` | `/api/auth/google` | Google OAuth |
| `GET` | `/api/auth/me` | Get current user |

### CV Screening
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cv/upload` | Upload PDF & get evaluation |
| `GET` | `/api/cv/health` | Health check |

## 🛣️ Roadmap

- [x] **Phase 1**: Authentication (JWT + Email/Password + Google OAuth)
- [x] **Phase 2**: Database layer (PostgreSQL + pgvector)
- [x] **Phase 3**: LangChain integration
- [x] **Phase 4**: Multi-agent architecture
- [x] **Phase 5**: Notifications (Email + WhatsApp)
- [x] **Phase 6**: Semantic search & CV comparison
- [x] **Phase 7**: Custom evaluation templates
- [x] **Phase 8**: Testing & CI/CD (329 tests, GitHub Actions)

✅ **All planned features complete! Ready for deployment.**

## 📝 License

MIT

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
