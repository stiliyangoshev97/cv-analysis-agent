# CV Screening Agent - Backend Runbook 📋

Quick reference for all backend commands. For detailed setup, see [README.md](README.md).

---

## 🚀 Server Commands

### Development Server
```bash
# Start with auto-reload (default port 8000)
uvicorn app.main:app --reload

# Custom port
uvicorn app.main:app --reload --port 8080

# With specific host (for Docker/remote access)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode (no reload, multiple workers)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation
```bash
# Start server then visit:
# Swagger UI:    http://localhost:8000/docs
# ReDoc:         http://localhost:8000/redoc
# OpenAPI JSON:  http://localhost:8000/openapi.json
```

---

## 🧪 Testing Commands

### Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
# Basic run
pytest

# Verbose output
pytest -v

# Very verbose (shows test docstrings)
pytest -vv

# Quiet mode (dots only)
pytest -q
```

### Run Specific Test Files
```bash
# Single file
pytest app/tests/unit/test_auth.py
pytest app/tests/integration/test_cv_api.py

# Multiple files
pytest app/tests/unit/test_auth.py app/tests/unit/test_cv_service.py

# Run by pattern
pytest app/tests/unit/test_*.py
pytest app/tests/integration/
```

### Run Specific Test Classes or Functions
```bash
# Single test function
pytest app/tests/unit/test_auth.py::test_password_hashing

# Single test class
pytest app/tests/integration/test_cv_api.py::TestUploadCV

# Single method in a class
pytest app/tests/integration/test_cv_api.py::TestUploadCV::test_upload_success
```

### Run Tests by Marker
```bash
# Run only async tests
pytest -m asyncio

# Run integration tests only
pytest app/tests/integration/
```

### Test Output Options
```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show slowest N tests
pytest --durations=10

# Show local variables in tracebacks
pytest -l

# Short traceback
pytest --tb=short

# No traceback
pytest --tb=no
```

### Coverage Reports
```bash
# Run with coverage
pytest --cov=app

# Coverage with missing lines
pytest --cov=app --cov-report=term-missing

# HTML coverage report
pytest --cov=app --cov-report=html
# Then open htmlcov/index.html

# Coverage for specific module
pytest --cov=app/features/cv --cov-report=term-missing
```

### Parallel Testing (if pytest-xdist installed)
```bash
# Run tests in parallel (auto-detect CPUs)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Rate Limit Testing
```bash
# Test rate limiting against a running server
# Start the server first: uvicorn app.main:app --reload

# Test public endpoints only (no auth needed)
python scripts/test_rate_limits.py

# Test specific tier
python scripts/test_rate_limits.py --tier auth      # 5/min - login endpoint
python scripts/test_rate_limits.py --tier public    # 60/min - health endpoint

# Test authenticated endpoints (requires valid credentials)
python scripts/test_rate_limits.py --email user@test.com --password mypass --tier all

# Test all tiers
python scripts/test_rate_limits.py --tier all --email user@test.com --password mypass

# Verbose output (show every request)
python scripts/test_rate_limits.py -v

# Custom server URL
python scripts/test_rate_limits.py --base-url http://localhost:8080
```

**Rate Limit Tiers:**
| Tier | Limit | Endpoint | What it tests |
|------|-------|----------|---------------|
| `auth` | 5/min | `/api/auth/login` | Sends wrong credentials (401) |
| `public` | 60/min | `/api/cv/health` | Hits health check |
| `default` | 100/min | `/api/profiles/` | Authenticated list (needs token) |
| `chat` | 30/min | `/api/chat/{id}` | Authenticated chat (needs token) |
| `upload` | 100/hour | `/api/cv/upload` | Sends invalid file (needs token) |
| `notification_test` | 5/hour | `/api/notifications/test/email` | Authenticated (needs token) |

---

## 🗄️ Database Commands

### Alembic Migrations
```bash
# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base

# View migration history
alembic history

# View current revision
alembic current

# Generate new migration (after model changes)
alembic revision --autogenerate -m "description_of_changes"

# Create empty migration (for custom SQL)
alembic revision -m "manual_migration_name"
```

### Database Setup
```bash
# Create database (PostgreSQL)
createdb cv_screening_agent

# Enable pgvector extension
psql cv_screening_agent -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Drop database (CAUTION!)
dropdb cv_screening_agent
```

### Seed Data
```bash
# Run seed script (creates system templates)
python -m app.db.seed

# Seed 20 evaluation profile templates (from project root)
cd backend && python ../seed_profiles.py
```

### Database Connection Test
```bash
# Test connection via Python
python -c "from app.db.session import engine; print('Connected!')"
```

---

## 📦 Dependency Management

### Install Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Test dependencies
pip install -r requirements-test.txt

# Both
pip install -r requirements.txt -r requirements-test.txt
```

### Update Dependencies
```bash
# Upgrade all packages
pip install --upgrade -r requirements.txt

# Freeze current versions
pip freeze > requirements-frozen.txt
```

### Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate

# Deactivate
deactivate
```

---

## 🔧 Development Utilities

### Linting & Formatting (if configured)
```bash
# Ruff (fast linter)
ruff check app/
ruff check app/ --fix

# Black (formatter)
black app/

# isort (import sorting)
isort app/

# Type checking with mypy
mypy app/
```

### Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Verify env loading
python -c "from app.config import get_settings; print(get_settings())"
```

### Generate Encryption Key
```bash
# Generate a valid Fernet encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Generate JWT Secret
```bash
# Generate a secure random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐳 Docker Commands (if using Docker)

```bash
# Build image
docker build -t cv-screening-backend .

# Run container
docker run -p 8000:8000 --env-file .env cv-screening-backend

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f backend
```

---

## 📊 Quick Reference

| Task | Command |
|------|---------|
| Start server | `uvicorn app.main:app --reload` |
| Run all tests | `pytest` |
| Run tests verbose | `pytest -v` |
| Run with coverage | `pytest --cov=app` |
| Apply migrations | `alembic upgrade head` |
| New migration | `alembic revision --autogenerate -m "msg"` |
| Seed database | `python -m app.db.seed` |
| Seed profiles | `cd backend && python ../seed_profiles.py` |
| Install deps | `pip install -r requirements.txt` |
| Install test deps | `pip install -r requirements-test.txt` |
