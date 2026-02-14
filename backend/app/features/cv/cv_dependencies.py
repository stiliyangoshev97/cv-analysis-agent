"""CV feature dependencies for FastAPI.

This module provides FastAPI dependencies specific to the CV feature.
Dependencies are used for dependency injection in route handlers.

Dependencies:
    get_cv_service: Inject CVService instance with database session.
    get_similarity_service: Inject SimilarityService for vector search.
    get_evaluation_service: Inject EvaluationService instance (legacy).
    get_pdf_service: Inject PDFService class.

Example:
    Using dependencies in routes::
    
        from .cv_dependencies import get_cv_service, get_similarity_service
        
        @router.post("/upload")
        async def upload(
            file: UploadFile,
            cv_service: CVService = Depends(get_cv_service)
        ):
            return await cv_service.process_and_evaluate(...)
        
        @router.get("/{cv_id}/similar")
        async def find_similar(
            cv_id: UUID,
            similarity_service: SimilarityService = Depends(get_similarity_service)
        ):
            return await similarity_service.find_similar_cvs(...)
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from .cv_service import CVService
from .similarity_service import SimilarityService
from .services import EvaluationService, PDFService


async def get_cv_service(
    session: AsyncSession = Depends(get_db_session),
) -> CVService:
    """Dependency to inject CVService with database session.
    
    Creates a new CVService instance for each request with the
    request-scoped database session.
    
    Args:
        session: SQLAlchemy async session (injected).
    
    Returns:
        CVService instance with database access.
    
    Example:
        >>> @router.post("/upload")
        ... async def upload(
        ...     cv_service: CVService = Depends(get_cv_service)
        ... ):
        ...     return await cv_service.process_and_evaluate(
        ...         file_content=pdf_bytes,
        ...         filename=filename,
        ...         user_id=current_user.id
        ...     )
    """
    return CVService(session)


async def get_similarity_service(
    session: AsyncSession = Depends(get_db_session),
) -> SimilarityService:
    """Dependency to inject SimilarityService for vector search.
    
    Creates a new SimilarityService instance for each request.
    
    Args:
        session: SQLAlchemy async session (injected).
    
    Returns:
        SimilarityService instance with database access.
    
    Example:
        >>> @router.get("/{cv_id}/similar")
        ... async def find_similar(
        ...     cv_id: UUID,
        ...     similarity_service: SimilarityService = Depends(get_similarity_service)
        ... ):
        ...     return await similarity_service.find_similar_cvs(cv_id, user_id)
    """
    return SimilarityService(session)


def get_evaluation_service() -> EvaluationService:
    """Dependency to inject EvaluationService (legacy).
    
    Creates a new EvaluationService instance for each request.
    Consider using CVService instead which integrates LangChain.
    
    Returns:
        EvaluationService instance.
    
    Note:
        This is kept for backwards compatibility.
        New code should use CVService.process_and_evaluate().
    """
    return EvaluationService()


def get_pdf_service() -> type[PDFService]:
    """Dependency to inject PDFService class.
    
    Returns the PDFService class (static methods, no instance needed).
    
    Returns:
        PDFService class.
    """
    return PDFService
