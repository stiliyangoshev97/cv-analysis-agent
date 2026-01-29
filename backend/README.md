# CV Screening Agent - Backend

FastAPI backend that extracts text from uploaded PDF CVs and evaluates them using Claude AI.

## How It Works

1. **Upload** → PDF file received via REST API
2. **Extract** → Text extracted using `pdfplumber`
3. **Evaluate** → Claude AI scores the CV against defined criteria
4. **Response** → Structured JSON with pass/fail, score, and reasoning

## Evaluation Criteria

The AI evaluates each CV against **3 criteria**:

| Criteria | Requirement | What AI Looks For |
|----------|-------------|-------------------|
| **Education** | High School Diploma or higher | High School, GED, Associate's, Bachelor's, Master's, PhD, certifications |
| **Fintech Experience** | Finance, Banking, or Crypto background | Financial institutions, crypto exchanges, trading platforms, blockchain, DeFi |
| **Technical Skills** | TypeScript or Python proficiency | Direct mentions of TypeScript, Python, JavaScript, React, Node.js, FastAPI, Django |

### Scoring Logic

- Each criterion is worth ~33 points
- **PASS**: Score ≥ 60 AND at least 2/3 criteria met
- **FAIL**: Score < 60 OR fewer than 2 criteria met

## Commands

```bash
# Navigate to backend
cd backend

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key (edit .env file)
cp .env.example .env

# Start development server
uvicorn app.main:app --reload --port 8000
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cv/upload` | Upload PDF & get evaluation |
| `GET` | `/api/cv/health` | Health check |
| `GET` | `/docs` | Swagger UI |

**Base URL:** `http://localhost:8000`
