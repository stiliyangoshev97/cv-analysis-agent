"""CV Screening Agent - Main FastAPI Application.

A production-ready API for AI-powered CV evaluation. Provides endpoints
for user authentication, CV upload/evaluation, and RAG-powered chat.

Features:
    - User authentication (email/password, Google OAuth)
    - PDF CV upload and text extraction
    - AI-powered CV evaluation using Claude
    - RAG-powered chat for CV Q&A
    - Structured scorecard with pass/fail status
    - Rate limiting per user/endpoint type
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import get_settings
from .features import (
    auth_router,
    cv_router,
    chat_router,
    notification_router,
    profile_router,
    settings_router,
)
from .core.rate_limit import limiter, rate_limit_exceeded_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.app_name}")
    logger.info("🔑 User API key management enabled via /api/settings")
    logger.info("📋 Users configure their own LLM providers (OpenAI, Anthropic, Gemini)")
    logger.info(f"🌐 CORS enabled for: {settings.frontend_url}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CV Screening Agent")


# Create FastAPI application
app = FastAPI(
    title="CV Screening Agent",
    description="""
## CV Screening Agent

An AI-powered CV evaluation platform with customizable hiring profiles,
RAG-powered chat, and multi-channel notifications.

### Core Features

- **📄 CV Upload & Processing**: PDF/DOCX upload with intelligent text extraction
- **🤖 AI Evaluation**: Claude AI scores CVs against customizable criteria
- **💬 RAG Chat**: Ask questions about any CV with context-aware responses
- **📋 Hiring Profiles**: Create custom evaluation templates or clone system defaults
- **🔔 Notifications**: Email and WhatsApp alerts for qualified candidates
- **🛡️ Rate Limiting**: Tiered rate limits to ensure fair usage

### Rate Limits

| Endpoint Type | Limit | Scope |
|--------------|-------|-------|
| Auth (login, register) | 5/min | Per IP |
| CV Upload | 100/hour | Per User |
| Chat/RAG | 30/min | Per User |
| General API | 100/min | Per User |
| Public (health) | 60/min | Per IP |

### How It Works

1. **Create a Profile**: Define evaluation criteria (or use system defaults)
2. **Upload CVs**: PDF or DOCX files are processed and chunked
3. **AI Evaluation**: Claude scores each CV against your criteria
4. **Review Results**: Get detailed scorecards with pass/fail recommendations
5. **Ask Questions**: Chat with AI about any CV using RAG
6. **Get Notified**: Receive alerts when candidates meet your threshold

### API Modules

| Module | Description |
|--------|-------------|
| `/api/auth` | Authentication (JWT, Google OAuth) |
| `/api/cv` | CV upload, evaluation, and management |
| `/api/chat` | RAG-powered Q&A about CVs |
| `/api/profiles` | Hiring profile CRUD |
| `/api/notifications` | Email/WhatsApp notification settings |
| `/api/settings` | User API keys and LLM preferences |
""",
    version="0.14.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter

# Register rate limit exceeded exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(cv_router)
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(profile_router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(settings_router, prefix="/api", tags=["Settings"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "CV Screening Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/cv/health"
    }


@app.get("/health", tags=["Health"])
async def global_health():
    """Global health check endpoint."""
    return {"status": "healthy"}
