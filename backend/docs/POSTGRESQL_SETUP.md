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

---

## Understanding Alembic & Migrations

### What is Alembic?

**Alembic** is a database migration tool for SQLAlchemy. Think of it as version control for your database schema.

| Concept | Description |
|---------|-------------|
| **Migration** | A script that describes a database change (add table, add column, etc.) |
| **Revision** | A unique version identifier for each migration |
| **Upgrade** | Apply migrations to move the database forward |
| **Downgrade** | Revert migrations to move the database backward |

### Why Do We Need Migrations?

**MongoDB (schema-less):**
```javascript
// Just add a field - MongoDB doesn't care
user.phoneNumber = "+1234567890";
await user.save(); // Works immediately
```

**PostgreSQL (strict schema):**
```sql
-- The database enforces the schema
-- You CAN'T just add a field without altering the table
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20);
```

Alembic generates and runs these `ALTER TABLE` statements for you.

### Migration Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. EDIT MODEL                                                  │
│     backend/app/db/models/user.py                              │
│     Add: phone: Mapped[Optional[str]] = mapped_column(...)     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. GENERATE MIGRATION                                          │
│     alembic revision --autogenerate -m "add_phone_to_users"    │
│     Creates: alembic/versions/xxxx_add_phone_to_users.py       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. REVIEW MIGRATION (optional but recommended)                 │
│     Check the generated file to ensure it looks correct         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. APPLY MIGRATION                                             │
│     alembic upgrade head                                        │
│     Runs: ALTER TABLE users ADD COLUMN phone VARCHAR(20);       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. UPDATE PYDANTIC SCHEMA (if API needs the new field)         │
│     backend/app/features/auth/auth_schemas.py                   │
│     Add: phone: Optional[str] = None                            │
└─────────────────────────────────────────────────────────────────┘
```

### Common Alembic Commands

```bash
# Generate a new migration (auto-detects model changes)
alembic revision --autogenerate -m "description_of_change"

# Apply all pending migrations
alembic upgrade head

# Apply just the next migration
alembic upgrade +1

# Rollback the last migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Show current migration version
alembic current

# Show migration history
alembic history
```

### SQLAlchemy Models vs Pydantic Schemas

These are **two separate things** that don't auto-sync:

| SQLAlchemy Model | Pydantic Schema |
|------------------|-----------------|
| Defines **database structure** | Defines **API contract** |
| Lives in `db/models/` | Lives in `features/*/schemas.py` |
| Requires migration to change | Just edit the file |
| `User(Base)` | `UserResponse(BaseModel)` |

**Example - Adding a phone field:**

```python
# 1. SQLAlchemy Model (db/models/user.py) - NEEDS MIGRATION
class User(Base):
    # ...existing fields...
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

# 2. Pydantic Schema (features/auth/auth_schemas.py) - NO MIGRATION
class UserResponse(BaseModel):
    # ...existing fields...
    phone: Optional[str] = None  # Add for API response
```

### MongoDB vs PostgreSQL Mindset

| Aspect | MongoDB | PostgreSQL |
|--------|---------|------------|
| **Schema** | Flexible, defined in code | Strict, enforced by database |
| **Adding a field** | Just add it | Migration required |
| **Data integrity** | Application's responsibility | Database enforces it |
| **Relationships** | Manual references, embedding | Foreign keys, JOINs |
| **Migrations** | Not needed | Essential |
| **Trade-off** | Faster development | Stronger guarantees |
