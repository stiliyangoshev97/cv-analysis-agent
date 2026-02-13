"""Feature modules for the CV Screening Agent.

This package contains all feature modules organized by domain.
Each feature is self-contained with its own router, schemas,
services, and dependencies.

Features:
    auth: User authentication (email/password, Google OAuth)
    cv: CV upload and AI-powered evaluation
    chat: RAG-powered chat for CV Q&A
"""

from .auth import auth_router
from .cv import cv_router
from .chat import chat_router

__all__ = ["auth_router", "cv_router", "chat_router"]

