# CV Screening Agent 🤖📄

An AI-powered CV screening platform that evaluates resumes against modern hiring criteria using Claude AI. Built for AI-first fintech companies looking for candidates who embrace modern development practices.

## 🎯 What It Does

Upload a PDF resume and get an instant AI-powered evaluation with:
- **Pass/Fail status** with confidence score (0-100)
- **5 evaluation criteria** tailored for modern tech roles
- **Detailed reasoning** explaining the AI's decision
- **Candidate name extraction** for quick reference

## 📊 Evaluation Criteria

| Criterion | Points | What We Look For |
|-----------|--------|------------------|
| **Education** | 15 | High School+, bootcamps, self-taught with portfolio |
| **Fintech Experience** | 20 | Finance, banking, crypto, DeFi, fintech startups |
| **Technical Skills** | 25 | TypeScript, Python, React, Node.js, FastAPI |
| **Soft Skills & Adaptability** | 20 | Fast learner, work under pressure, team player |
| **AI-Native Development** | 20 | AI coding tools, RAG, MCP, AI agents |

### AI-Native Development Criteria (What Sets This Apart)
We specifically look for candidates who:
- Use **AI coding tools**: Claude Code, GitHub Copilot, Cursor, Windsurf
- Practice **vibe coding**: AI pair programming, prompt engineering
- Understand **RAG systems**: Vector databases, embeddings, retrieval
- Know **MCP**: Model Context Protocol, tool-use, function calling
- Can build **AI agents**: LangChain, LlamaIndex, autonomous systems
- Have **LLM integration** experience: OpenAI, Anthropic APIs in production

### Pass/Fail Logic
- ✅ **PASS**: Score ≥ 60 AND 3+ criteria met (must include Technical Skills)
- ❌ **FAIL**: Score < 60 OR fewer than 3 criteria OR no Technical Skills

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ with pip
- Node.js 18+ with npm
- Anthropic API key ([get one here](https://console.anthropic.com/))

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your API key
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

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
| **pdfplumber** | PDF text extraction |
| **Anthropic SDK** | Claude AI integration |
| **Pydantic** | Data validation & schemas |
| **python-jose** | JWT authentication |
| **bcrypt** | Password hashing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI library |
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
- [x] **Phase 1.5**: Project restructuring (Controller-Service-Model pattern)
- [ ] **Phase 2**: Database layer (PostgreSQL + pgvector)
- [ ] **Phase 3**: LangChain integration
- [ ] **Phase 4**: Multi-agent architecture
- [ ] **Phase 5**: Notifications (Email + WhatsApp)
- [ ] **Phase 6**: Dashboard & semantic search
- [ ] **Phase 7**: Candidate match-up & comparison

## 📝 License

MIT

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
