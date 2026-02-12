"""CV Screening feature module.

This module provides CV upload, processing, and AI-powered evaluation
functionality for the CV Screening Agent.

Architecture (Controller-Service-Model Pattern):
    - cv_routes.py: Route definitions (thin)
    - cv_controller.py: HTTP request/response handling
    - cv_service.py: Orchestration and business logic
    - cv_schemas.py: Pydantic validation schemas
    - cv_models.py: CV model (Phase 2: SQLAlchemy)
    - cv_dependencies.py: FastAPI dependencies
    - services/: Specialized services
        - pdf_service.py: PDF text extraction
        - evaluation_service.py: AI-powered evaluation

Exports:
    cv_router: FastAPI router with CV endpoints.
    CVService: Orchestration service.
    PDFService: PDF processing service.
    EvaluationService: AI evaluation service.
"""

from .cv_routes import router as cv_router
from .cv_service import CVService
from .cv_schemas import (
    CVEvaluationResponse,
    CVEvaluationRequest,
    EvaluationCriteria,
    PassFailStatus,
    UploadResponse,
    ErrorResponse,
)
from .services.pdf_service import PDFService
from .services.evaluation_service import EvaluationService

__all__ = [
    # Router
    "cv_router",
    # Services
    "CVService",
    "PDFService",
    "EvaluationService",
    # Schemas
    "CVEvaluationResponse",
    "CVEvaluationRequest",
    "EvaluationCriteria",
    "PassFailStatus",
    "UploadResponse",
    "ErrorResponse",
]
