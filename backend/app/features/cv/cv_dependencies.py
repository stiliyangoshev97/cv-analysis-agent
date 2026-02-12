"""CV feature dependencies for FastAPI.

This module provides FastAPI dependencies specific to the CV feature.
Dependencies are used for dependency injection in route handlers.

Dependencies:
    get_cv_service: Inject CVService instance.
    get_evaluation_service: Inject EvaluationService instance.
    get_pdf_service: Inject PDFService class.

Example:
    Using dependencies in routes::
    
        from .cv_dependencies import get_cv_service
        
        @router.post("/upload")
        async def upload(
            file: UploadFile,
            cv_service: CVService = Depends(get_cv_service)
        ):
            return await cv_service.process_cv(...)
"""

from .cv_service import CVService
from .services import EvaluationService, PDFService


def get_cv_service() -> CVService:
    """Dependency to inject CVService.
    
    Creates a new CVService instance for each request.
    CVService orchestrates PDF processing and AI evaluation.
    
    Returns:
        CVService instance.
    
    Example:
        >>> @router.post("/upload")
        ... async def upload(
        ...     cv_service: CVService = Depends(get_cv_service)
        ... ):
        ...     return await cv_service.process_cv(pdf_bytes, filename)
    """
    return CVService()


def get_evaluation_service() -> EvaluationService:
    """Dependency to inject EvaluationService.
    
    Creates a new EvaluationService instance for each request.
    
    Returns:
        EvaluationService instance.
    
    Example:
        >>> @router.post("/evaluate")
        ... async def evaluate(
        ...     service: EvaluationService = Depends(get_evaluation_service)
        ... ):
        ...     return service.evaluate_cv(text, filename)
    """
    return EvaluationService()


def get_pdf_service() -> type[PDFService]:
    """Dependency to inject PDFService class.
    
    Returns the PDFService class (static methods, no instance needed).
    
    Returns:
        PDFService class.
    """
    return PDFService
