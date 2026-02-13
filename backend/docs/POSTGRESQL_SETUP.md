# PostgreSQL Setup Guide for CV Screening Agent

## Option 1: Install via Homebrew (Recommended for macOS)

```bash
# Install PostgreSQL 17 (required for pgvector compatibility)
brew install postgresql@17

# Start PostgreSQL service
brew services start postgresql@17

# Add to PATH (add to ~/.zshrc for persistence)
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"

# Create the database
createdb cv_screening_agent

# Install and enable pgvector extension
brew install pgvector
psql cv_screening_agent -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Database URL Configuration

On macOS with Homebrew, PostgreSQL uses your system username without password:
```bash
# In backend/.env
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/cv_screening_agent
```

For example, if your username is "john":
```
DATABASE_URL=postgresql+asyncpg://john@localhost:5432/cv_screening_agent
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
  pgvector/pgvector:pg17

# The pgvector extension is pre-installed in this image

# For Docker, use this connection string:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cv_screening_agent
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

1. Install dependencies:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

2. Run migrations:
```bash
./venv/bin/alembic upgrade head
```

3. Seed the database with system templates:
```bash
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.db.seed import seed_system_templates

async def run_seed():
    async with AsyncSessionLocal() as session:
        await seed_system_templates(session)
        print('Seeding complete!')

asyncio.run(run_seed())
"
```

4. Verify the database:
```bash
psql cv_screening_agent -c "\dt"
```

You should see all 11 tables:
- alembic_version
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

## Troubleshooting

### "role postgres does not exist" error
On macOS with Homebrew, use your system username instead of "postgres":
```bash
# Check your username
whoami

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://YOUR_USERNAME@localhost:5432/cv_screening_agent
```

### pgvector extension not found
Make sure you're using PostgreSQL 17 (pgvector is compiled for 17 and 18):
```bash
brew services stop postgresql@16  # Stop old version if running
brew services start postgresql@17
```

### Connection refused
Make sure PostgreSQL service is running:
```bash
brew services list | grep postgresql
```
