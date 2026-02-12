"""Feature modules for the CV Screening Agent.

This package contains all feature modules organized by domain.
Each feature is self-contained with its own router, schemas,
services, and dependencies.

Features:
    auth: User authentication (email/password, Google OAuth)
    cv: CV upload and AI-powered evaluation
"""

from .auth import auth_router
from .cv import cv_router

__all__ = ["auth_router", "cv_router"]

