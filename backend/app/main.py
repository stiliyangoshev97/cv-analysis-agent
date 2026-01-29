"""
CV Screening Agent - Main FastAPI Application.
A production-ready API for AI-powered CV evaluation.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers import cv_router

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
    
    if not settings.anthropic_api_key or settings.anthropic_api_key == "your_anthropic_api_key_here":
        logger.warning("⚠️  ANTHROPIC_API_KEY not configured! Please set it in .env file.")
    else:
        logger.info("✅ Anthropic API key configured")
    
    logger.info(f"Using model: {settings.claude_model}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CV Screening Agent")


# Create FastAPI application
app = FastAPI(
    title="CV Screening Agent",
    description="""
    ## XBO.com Internal CV Screening Agent
    
    An AI-powered CV evaluation system that screens candidates based on:
    
    - **Education**: High School Diploma or higher
    - **Fintech Experience**: Finance, Banking, or Crypto background
    - **Technical Skills**: TypeScript or Python proficiency
    
    ### How it works:
    1. Upload a PDF CV
    2. Text is extracted from the PDF
    3. AI evaluates the CV against our criteria
    4. Receive a structured scorecard with pass/fail status
    """,
    version="1.0.0",
    lifespan=lifespan
)

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
app.include_router(cv_router)


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
