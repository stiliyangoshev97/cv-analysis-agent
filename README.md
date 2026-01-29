# CV Screening Agent

An AI-powered CV screening application that evaluates resumes against predefined hiring criteria using Claude AI.

## How It Works

1. **Upload** - User uploads a PDF CV via drag & drop or file picker
2. **Extract** - Backend extracts text content from the PDF
3. **Evaluate** - Claude AI analyzes the CV against 3 criteria:
   - Education (High School Diploma or higher)
   - Fintech Experience (Finance, Banking, or Crypto background)
   - Technical Skills (TypeScript or Python proficiency)
4. **Display** - Frontend shows a scorecard with pass/fail status, score, and detailed reasoning

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python | Runtime |
| FastAPI | REST API framework |
| pdfplumber | PDF text extraction |
| Anthropic SDK | Claude AI integration |
| Pydantic | Data validation |

### Frontend
| Technology | Purpose |
|------------|---------|
| React | UI library |
| TypeScript | Type safety |
| Vite | Build tool |
| Tailwind CSS | Styling |
| TanStack Query | Server state |
| Axios | HTTP client |

## Quick Start

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your Anthropic API key to .env
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Open App

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Running the Servers

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

## Project Structure

```
CV Analysis Agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment settings
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── services/            # PDF & AI services
│   │   └── routers/             # API endpoints
│   ├── .env                     # API keys (not committed)
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/ui/       # Reusable components
    │   ├── features/            # Feature modules
    │   ├── lib/api.ts           # API client
    │   └── types/               # TypeScript types
    └── package.json
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cv/upload` | Upload PDF and get evaluation |
| `GET` | `/api/cv/health` | Health check |
