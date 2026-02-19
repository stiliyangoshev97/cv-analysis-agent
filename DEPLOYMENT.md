# Deployment Guide 🚀

This guide explains how to deploy the CV Analysis Agent to **Render** (backend + PostgreSQL) and **Vercel** (frontend).

**Last Updated:** February 20, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Render Deployment (Backend)](#render-deployment-backend)
3. [Vercel Deployment (Frontend)](#vercel-deployment-frontend)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Environment Variables Reference](#environment-variables-reference)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- [ ] GitHub repository with your code pushed
- [ ] Render account (https://render.com)
- [ ] Vercel account (https://vercel.com)
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

Save these values securely - you'll need them for environment variables.

---

## Render Deployment (Backend)

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `cv-agent-db`
   - **Database**: `cv_agent`
   - **User**: `cv_agent_user`
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 16
   - **Plan**: Free (for testing) or Starter ($7/mo for production)
4. Click **Create Database**
5. Wait for database to be ready (1-2 minutes)
6. Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 2: Enable pgvector Extension

After the database is created:

1. Go to your database in Render Dashboard
2. Click **Shell** tab (or use `psql` with External URL)
3. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

> **Note**: Render PostgreSQL supports pgvector out of the box on paid plans. For free tier, you may need to check availability.

### Step 3: Create Web Service (Backend)

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `cv-agent-backend` |
| **Region** | Same as database |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (testing) or Starter ($7/mo) |

### Step 4: Configure Environment Variables

In the Render web service settings, add these environment variables:

#### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | **Important**: Change `postgresql://` to `postgresql+asyncpg://` from the Render-provided URL |
| `JWT_SECRET_KEY` | `<your-generated-key>` | From `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | `<your-generated-key>` | From `openssl rand -base64 32` |
| `ENVIRONMENT` | `production` | Enables production settings |
| `SECRET_KEY` | `<your-generated-key>` | Same as JWT_SECRET_KEY |

#### Optional Variables (Google OAuth)

| Variable | Value |
|----------|-------|
| `GOOGLE_OAUTH_CLIENT_ID` | Your Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Your Google OAuth client secret |

#### CORS Configuration

| Variable | Value |
|----------|-------|
| `CORS_ORIGINS` | `https://your-app.vercel.app,http://localhost:5173` |

### Step 5: Deploy and Run Migrations

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

### Step 6: Verify Backend

Visit your Render URL:
- `https://your-app.onrender.com/health` - Should return `{"status": "healthy"}`
- `https://your-app.onrender.com/docs` - Swagger API documentation

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
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
JWT_SECRET_KEY=your-64-char-hex-string
ENCRYPTION_KEY=your-32-byte-base64-string
SECRET_KEY=your-64-char-hex-string
ENVIRONMENT=production

# === Google OAuth (Optional) ===
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# === CORS ===
CORS_ORIGINS=https://your-app.vercel.app

# === JWT Settings (Optional, with defaults) ===
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# === LLM Defaults (Optional) ===
CLAUDE_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=text-embedding-3-small

# === Email Notifications (Optional - users can use BYOK) ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=CV Analysis Agent
SMTP_USE_TLS=true

# === WhatsApp (Optional - users can use BYOK) ===
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=+14155238886
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

1. Verify `DATABASE_URL` uses `postgresql+asyncpg://` (not just `postgresql://`)
2. Check that pgvector extension is installed
3. Ensure migrations have been run: `alembic upgrade head`

#### "CORS error" in browser

1. Check `CORS_ORIGINS` includes your Vercel domain
2. Redeploy after changing environment variables
3. Verify no trailing slash in the origin URL

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

### Render

| Resource | Free Tier | Starter |
|----------|-----------|---------|
| Web Service | 750 hours/month | $7/month |
| PostgreSQL | 90 days, then paused | $7/month |
| **Total** | $0 (limited) | ~$14/month |

### Vercel

| Plan | Limit | Cost |
|------|-------|------|
| Hobby | 100GB bandwidth | $0 |
| Pro | Unlimited | $20/month |

### AI API Costs (User's BYOK)

Users pay for their own API usage:

| Provider | Model | Approximate Cost |
|----------|-------|------------------|
| OpenAI | text-embedding-3-small | ~$0.02 per 1M tokens |
| Anthropic | Claude Sonnet | ~$3 per 1M input tokens |
| OpenAI | GPT-4.1 | ~$2 per 1M input tokens |

---

## Quick Deploy Checklist

### Render (Backend)

- [ ] Create PostgreSQL database
- [ ] Enable pgvector extension
- [ ] Create Web Service
- [ ] Set all required environment variables
- [ ] Deploy and run `alembic upgrade head`
- [ ] Verify `/health` endpoint

### Vercel (Frontend)

- [ ] Create project from GitHub
- [ ] Set `VITE_API_URL` to Render URL
- [ ] Set `VITE_GOOGLE_CLIENT_ID` (if using OAuth)
- [ ] Deploy

### Post-Deploy

- [ ] Update CORS origins in Render
- [ ] Update Google OAuth redirect URIs
- [ ] Test user registration/login
- [ ] Test CV upload and evaluation
- [ ] Test notifications (optional)

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review Render/Vercel deployment logs
3. Test locally to isolate the issue
4. Check GitHub Issues for known problems

Happy deploying! 🚀
