"""CV Screening feature module.

This module provides CV upload, processing, and AI-powered evaluation
functionality for the CV Screening Agent.

Architecture (Controller-Service-Repository Pattern):
    - cv_routes.py: Route definitions (thin)
    - cv_controller.py: HTTP request/response handling
    - cv_service.py: Orchestration and business logic
    - similarity_service.py: Vector similarity search
    - cv_schemas.py: Pydantic validation schemas
    - cv_repository.py: CV database operations
    - evaluation_repository.py: Evaluation database operations
    - template_repository.py: Template database operations
    - embedding_repository.py: Vector embedding operations (pgvector)
    - cv_dependencies.py: FastAPI dependencies
    - services/: Specialized services
        - pdf_service.py: PDF text extraction
        - evaluation_service.py: AI-powered evaluation

Note:
    Chat functionality has moved to features/chat/ for clean separation.

Exports:
    cv_router: FastAPI router with CV endpoints.
    CVService: Orchestration service.
    SimilarityService: Vector similarity search service.
    PDFService: PDF processing service.
    EvaluationService: AI evaluation service.
"""

from .cv_routes import router as cv_router
from .cv_service import CVService, ProcessingResult
from .similarity_service import (
    SimilarityService,
    SimilarCVResult,
    CVRankingResult,
    CVComparisonResult,
)
from .cv_schemas import (
    CVEvaluationResponse,
    CVEvaluationRequest,
    EvaluationCriteria,
    PassFailStatus,
    UploadResponse,
    ErrorResponse,
    CVSummary,
    CVListResponse,
    CVDetailResponse,
    EvaluationDetail,
    # Similarity schemas
    SimilarCVResponse,
    SimilarCVsResponse,
    CVRankingResponse,
    CVCompareRequest,
    CVCompareResponse,
    CVComparisonItemResponse,
    CVSearchRequest,
    CVSearchResponse,
)
from .services.pdf_service import PDFService
from .services.evaluation_service import EvaluationService

# Repositories
from .cv_repository import CVRepository
from .evaluation_repository import EvaluationRepository
from .template_repository import TemplateRepository
from .embedding_repository import EmbeddingRepository, SimilarityResult

__all__ = [
    # Router
    "cv_router",
    # Services
    "CVService",
    "ProcessingResult",
    "SimilarityService",
    "SimilarCVResult",
    "CVRankingResult",
    "CVComparisonResult",
    "PDFService",
    "EvaluationService",
    # Repositories
    "CVRepository",
    "EvaluationRepository",
    "TemplateRepository",
    "EmbeddingRepository",
    # Data Classes
    "SimilarityResult",
    # Schemas
    "CVEvaluationResponse",
    "CVEvaluationRequest",
    "EvaluationCriteria",
    "PassFailStatus",
    "UploadResponse",
    "ErrorResponse",
    "CVSummary",
    "CVListResponse",
    "CVDetailResponse",
    "EvaluationDetail",
    # Similarity Schemas
    "SimilarCVResponse",
    "SimilarCVsResponse",
    "CVRankingResponse",
    "CVCompareRequest",
    "CVCompareResponse",
    "CVComparisonItemResponse",
    "CVSearchRequest",
    "CVSearchResponse",
]
