# PostgreSQL Setup Guide for CV Screening Agent

## Option 1: Install via Homebrew (Recommended for macOS)

```bash
# Install PostgreSQL 16
brew install postgresql@16

# Start PostgreSQL service
brew services start postgresql@16

# Add to PATH (add to ~/.zshrc for persistence)
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

# Create the database
createdb cv_screening_agent

# Enable pgvector extension (install first if needed)
brew install pgvector

# Connect and enable extension
psql cv_screening_agent -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Option 2: Install via Docker

```bash
# Pull and run PostgreSQL with pgvector
docker run -d \
  --name cv-screening-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=cv_screening_agent \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# The pgvector extension is pre-installed in this image
```

## Option 3: Use a Cloud Provider

### Supabase (Free tier available)
1. Go to https://supabase.com
2. Create a new project
3. Enable pgvector extension in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Get connection string from Settings > Database
5. Update `backend/.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```

### Neon (Free tier available)
1. Go to https://neon.tech
2. Create a new project
3. Enable pgvector in SQL Editor
4. Get connection string and update `.env`

## After PostgreSQL is Running

1. Run migrations:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

2. Verify the database:
```bash
psql cv_screening_agent -c "\dt"
```

You should see all 10 tables:
- users
- user_api_keys
- user_agent_configs
- evaluation_templates
- template_criteria
- cvs
- cv_evaluations
- cv_embeddings
- chat_history
- notification_settings
