# Deployment Guide 🚀

This guide explains how to deploy the CV Analysis Agent to **Neon** (PostgreSQL + pgvector), **Render** (backend), and **Vercel** (frontend).

**Last Updated:** February 20, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Neon Setup (PostgreSQL Database)](#neon-setup-postgresql-database)
4. [Render Deployment (Backend)](#render-deployment-backend)
5. [Vercel Deployment (Frontend)](#vercel-deployment-frontend)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Environment Variables Reference](#environment-variables-reference)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- [ ] GitHub repository with your code pushed
- [ ] Neon account (https://neon.tech) — free, for PostgreSQL + pgvector
- [ ] Render account (https://render.com) — free, for backend hosting
- [ ] Vercel account (https://vercel.com) — free, for frontend hosting
- [ ] Google Cloud Console project for OAuth (optional)
- [ ] All 329 tests passing locally (`cd backend && pytest`)

### Generate Required Secrets

You'll need these values for deployment:

```bash
# Generate JWT secret key (32 bytes hex)
openssl rand -hex 32

# Generate encryption key (32 bytes base64)
openssl rand -base64 32
```

Save these values securely — you'll need them for environment variables.

---

## Architecture Overview

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Vercel     │────▶│  Render (FastAPI) │────▶│  Neon (Postgres) │
│   Frontend   │     │  Backend          │     │  + pgvector      │
│   (React)    │     │  (Python)         │     │  (AWS Frankfurt) │
└──────────────┘     └──────────────────┘     └──────────────────┘
```

**Why Neon instead of Render PostgreSQL?**

- Render's free-tier PostgreSQL does **not support pgvector**, which is required for CV embedding and similarity search
- Neon's free tier includes pgvector out of the box
- Neon free tier **never expires** (Render's free DB expires after 90 days)
- Neon provides 0.5 GB storage and 191 compute hours/month for free

---

## Neon Setup (PostgreSQL Database)

### Step 1: Create a Neon Project

1. Go to [Neon Console](https://console.neon.tech)
2. Click **New Project**
3. Configure:

| Setting | Value |
|---------|-------|
| **Project name** | `cv-agent` |
| **Postgres version** | `17` (matches local development) |
| **Cloud provider** | `AWS` |
| **Region** | `AWS Europe Central 1 (Frankfurt)` — same region as Render |
| **Neon Auth** | Disabled (app has its own auth) |

4. Click **Create Project**

### Step 2: Enable pgvector Extension

1. In the Neon dashboard, go to **SQL Editor** (left sidebar)
2. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. You should see: `CREATE EXTENSION` — pgvector is now enabled

### Step 3: Get the Connection String

1. Go to **Dashboard** → **Connection Details**
2. Copy the **Connection string** — it looks like:
   ```
   postgresql://neondb_owner:abc123@ep-cool-name-12345-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
   ```

### Step 4: Convert the Connection String

The app uses `asyncpg` (async PostgreSQL driver), which requires a different URL format:

| What to change | From | To |
|---------------|------|-----|
| **Driver prefix** | `postgresql://` | `postgresql+asyncpg://` |
| **Remove `channel_binding`** | `&channel_binding=require` | *(remove entirely)* |
| **Keep `sslmode`** | `?sslmode=require` | `?sslmode=require` *(no change)* |

**Why?** SQLAlchemy needs the `+asyncpg` driver suffix to use async connections. The `asyncpg` driver supports `sslmode=require` natively. However, the `channel_binding` parameter is libpq-specific and **not supported** by asyncpg — it must be removed.

**Example conversion:**
```
# Neon provides:
postgresql://neondb_owner:abc123@ep-cool-name-12345-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Convert to (change prefix, remove channel_binding):
postgresql+asyncpg://neondb_owner:abc123@ep-cool-name-12345-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

Save this converted URL — you'll use it as `DATABASE_URL` in the Render backend.

---

## Render Deployment (Backend)

### Step 1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. In your existing project, click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `cv-agent-backend` |
| **Region** | `Frankfurt (EU Central)` — same as Neon |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (testing) or Starter ($7/mo) |

### Step 2: Configure Environment Variables

In the Render web service settings, add these environment variables:

#### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...?sslmode=require` | Your converted Neon connection string (see [Step 4 above](#step-4-convert-the-connection-string)) |
| `JWT_SECRET_KEY` | `<your-generated-key>` | From `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | `<your-generated-key>` | From `openssl rand -base64 32` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Your Vercel frontend URL (update after Vercel deploy) |
| `FRONTEND_URL` | `https://your-app.vercel.app` | Same as above (used for OAuth redirects) |
| `DEBUG` | `false` | Disable debug mode in production |

#### Optional Variables (Google OAuth)

| Variable | Value |
|----------|-------|
| `GOOGLE_CLIENT_ID` | Your Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth client secret |

### Step 3: Deploy and Run Migrations

1. Click **Create Web Service**
2. Wait for initial deployment (5-10 minutes)
3. Once deployed, open the **Shell** tab and run:
   ```bash
   alembic upgrade head
   ```
4. (Optional) Seed system templates:
   ```bash
   python -m app.db.seed
   ```

### Step 4: Verify Backend

Visit your Render URL:
- `https://your-app.onrender.com/health` — Should return `{"status": "healthy"}`
- `https://your-app.onrender.com/docs` — Swagger API documentation

---

## Vercel Deployment (Frontend)

### Step 1: Create Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` (auto-detected) |
| **Output Directory** | `dist` (auto-detected) |

### Step 2: Configure Environment Variables

Add these in the Vercel project settings under **Settings** → **Environment Variables**:

| Variable | Value | Environment |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-app.onrender.com` | Production |
| `VITE_GOOGLE_CLIENT_ID` | Your Google OAuth client ID | Production |

> **Note**: For Preview deployments, you might want different values.

### Step 3: Deploy

1. Click **Deploy**
2. Wait for build to complete (2-3 minutes)
3. Your app will be available at `https://your-project.vercel.app`

### Security Headers

The `frontend/vercel.json` file is already configured with security headers:

- ✅ Content-Security-Policy (strict CSP)
- ✅ Strict-Transport-Security (HSTS)
- ✅ X-Frame-Options (clickjacking protection)
- ✅ X-Content-Type-Options (MIME sniffing protection)
- ✅ Cache headers for static assets

---

## Post-Deployment Configuration

### 1. Update CORS Origins

In Render, update the `CORS_ORIGINS` environment variable to include your Vercel domain:

```
https://your-project.vercel.app
```

Then redeploy the backend.

### 2. Update Google OAuth

If using Google OAuth, update your Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Credentials**
3. Edit your OAuth 2.0 Client ID
4. Add to **Authorized JavaScript origins**:
   ```
   https://your-project.vercel.app
   ```
5. Add to **Authorized redirect URIs**:
   ```
   https://your-project.vercel.app
   https://your-project.vercel.app/auth/callback
   ```

### 3. Verify End-to-End

Test the following flows:

- [ ] User registration with email/password
- [ ] User login
- [ ] Google OAuth (if configured)
- [ ] API key configuration in Settings
- [ ] CV upload and evaluation
- [ ] Chat with AI about a CV
- [ ] Find similar candidates
- [ ] Notification settings (if SMTP/Twilio configured)

---

## Environment Variables Reference

### Backend (Render)

```env
# === Required ===
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
JWT_SECRET_KEY=your-64-char-hex-string
ENCRYPTION_KEY=your-32-byte-base64-string
CORS_ORIGINS=https://your-app.vercel.app
FRONTEND_URL=https://your-app.vercel.app
DEBUG=false

# === Google OAuth (Optional) ===
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# === JWT Settings (Optional, have defaults) ===
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend (Vercel)

```env
VITE_API_URL=https://your-app.onrender.com
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

---

## Troubleshooting

### Backend Issues

#### "Connection refused" or database errors

1. Verify `DATABASE_URL` uses `postgresql+asyncpg://` prefix (not just `postgresql://`)
2. Verify `channel_binding=require` has been removed from the URL
3. Keep `?sslmode=require` — asyncpg supports it natively
3. Check that pgvector extension is installed in Neon SQL Editor
4. Ensure migrations have been run: `alembic upgrade head`

#### "CORS error" in browser

1. Check `CORS_ORIGINS` includes your Vercel domain (no trailing slash)
2. Redeploy the backend after changing environment variables
3. Example: `CORS_ORIGINS=https://cv-agent.vercel.app`

#### "JWT decode error"

1. Ensure `JWT_SECRET_KEY` is the same across all instances
2. Check token hasn't expired

### Frontend Issues

#### "Failed to fetch" or API errors

1. Verify `VITE_API_URL` points to correct Render URL
2. Check backend health endpoint is responding
3. Verify CORS is configured correctly

#### Google OAuth not working

1. Check authorized origins in Google Cloud Console
2. Verify `VITE_GOOGLE_CLIENT_ID` matches console
3. Ensure redirect URIs are configured

### Neon-Specific

#### "SSL connection required" or SSL errors

Ensure your `DATABASE_URL` uses `?sslmode=require` (asyncpg supports this natively).

Remove `&channel_binding=require` if present — it's a libpq-specific parameter that asyncpg does not recognize.

#### pgvector not found

Run in Neon SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Render-Specific

#### Slow cold starts (free tier)

Free tier services spin down after 15 minutes of inactivity. First request after spin-down takes 30-60 seconds.

**Solution**: Upgrade to Starter plan ($7/mo) for always-on service.

#### Build failures

1. Check Python version compatibility
2. Verify all dependencies are in `requirements.txt`
3. Check Render build logs for specific errors

### Vercel-Specific

#### Build fails on TypeScript errors

Run locally first to catch issues:
```bash
cd frontend
npm run build
```

#### Environment variables not working

1. Prefix must be `VITE_` for client-side variables
2. Redeploy after adding/changing variables
3. Check they're set for the correct environment (Production/Preview)

---

## Cost Estimates

### Neon (Database)

| Plan | Storage | Compute | pgvector | Expiration | Cost |
|------|---------|---------|----------|------------|------|
| Free | 0.5 GB | 191 hrs/month | ✅ | Never | $0 |
| Launch | 10 GB | 300 hrs/month | ✅ | Never | $19/month |

### Render (Backend)

| Plan | Limit | Cost |
|------|-------|------|
| Free | 750 hours/month, sleeps after 15min | $0 |
| Starter | Always-on | $7/month |

### Vercel (Frontend)

| Plan | Limit | Cost |
|------|-------|------|
| Hobby | 100GB bandwidth | $0 |
| Pro | Unlimited | $20/month |

### Total (Free Tier)

| Service | Cost |
|---------|------|
| Neon | $0 |
| Render | $0 |
| Vercel | $0 |
| **Total** | **$0/month** |

### AI API Costs (User's BYOK)

Users pay for their own API usage:

| Provider | Model | Approximate Cost |
|----------|-------|------------------|
| OpenAI | text-embedding-3-small | ~$0.02 per 1M tokens |
| Anthropic | Claude Sonnet | ~$3 per 1M input tokens |
| OpenAI | GPT-4.1 | ~$2 per 1M input tokens |

---

## Quick Deploy Checklist

### Neon (Database)

- [ ] Create project (PostgreSQL 17, AWS Frankfurt)
- [ ] Enable pgvector: `CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] Copy and convert connection string (`postgresql+asyncpg://...?sslmode=require`)

### Render (Backend)

- [ ] Create Web Service (Root Dir: `backend`)
- [ ] Set all required environment variables
- [ ] Deploy and run `alembic upgrade head`
- [ ] Verify `/health` endpoint

### Vercel (Frontend)

- [ ] Create project from GitHub (Root Dir: `frontend`)
- [ ] Set `VITE_API_URL` to Render URL
- [ ] Set `VITE_GOOGLE_CLIENT_ID` (if using OAuth)
- [ ] Deploy

### Post-Deploy

- [ ] Update `CORS_ORIGINS` and `FRONTEND_URL` in Render with Vercel URL
- [ ] Update Google OAuth redirect URIs in Google Cloud Console
- [ ] Test user registration/login
- [ ] Test CV upload and evaluation
- [ ] Test notifications (optional)

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review Render/Vercel deployment logs
3. Check Neon dashboard for database connectivity
4. Test locally to isolate the issue
5. Check GitHub Issues for known problems

Happy deploying! 🚀
