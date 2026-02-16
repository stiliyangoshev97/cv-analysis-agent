# CV Screening Agent 🤖📄

An AI-powered CV screening platform that evaluates resumes against modern hiring criteria using frontier AI models. Built for AI-first fintech companies looking for candidates who embrace modern development practices.

**Version:** 0.15.5 | **Last Updated:** February 16, 2026

## 🎯 What It Does

Upload a PDF resume and get an instant AI-powered evaluation with:
- **Pass/Fail status** with confidence score (0-100)
- **5 evaluation criteria** tailored for modern tech roles
- **Detailed reasoning** explaining the AI's decision
- **Candidate name extraction** for quick reference
- **Multi-LLM support** - choose Anthropic, OpenAI, or Google Gemini

## 🤖 Supported AI Models (February 2026)

Choose your preferred AI provider and model in Settings:

### Anthropic Claude
| Model | Description | Best For |
|-------|-------------|----------|
| **Claude Opus 4.6** | Most intelligent model | Complex reasoning, research, deep analysis |
| **Claude Sonnet 4.5** | Balanced speed & intelligence | Daily coding, CV analysis, general tasks |
| **Claude Haiku 4.5** | Fastest with excellent quality | High-volume screening, quick responses |

### OpenAI GPT
| Model | Description | Best For |
|-------|-------------|----------|
| **GPT-5.2** | Best for coding & agents | Complex agentic tasks, coding |
| **GPT-5.2 Pro** | Smarter, more precise | When you need extra accuracy |
| **GPT-5 / Mini / Nano** | Configurable reasoning | Various speed/cost tradeoffs |
| **GPT-4.1** | Smartest non-reasoning | Reliable, fast responses |

### Google Gemini
| Model | Description | Best For |
|-------|-------------|----------|
| **Gemini 3 Pro** | Most intelligent, multimodal | Complex tasks, agentic use cases |
| **Gemini 3 Flash** | Balanced speed & scale | Production workloads |
| **Gemini 2.5 Pro** | Advanced thinking model | Complex reasoning, code, math |
| **Gemini 2.5 Flash** | Best price-performance | Large scale processing |

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
