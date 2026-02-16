"""CV routes configuration.

This module defines the FastAPI router for CV screening endpoints.
Routes are thin - they only wire up URL paths to controller handlers.

Rate Limits:
    - upload: 100/hour - BYOK users pay own costs
    - re-evaluate: 100/hour - BYOK users pay own costs
    - Other endpoints: 100/minute - Standard authenticated
    - health: 60/minute - Public endpoint

Routes:
    POST /api/cv/upload - Upload and evaluate a CV
    GET /api/cv/ - List user's CVs
    GET /api/cv/{cv_id} - Get CV details
    DELETE /api/cv/{cv_id} - Delete a CV
    POST /api/cv/{cv_id}/re-evaluate - Re-evaluate with different template
    GET /api/cv/health - Health check for CV service

Example:
    Including the router in the FastAPI app::
    
        from app.features.cv import cv_router
        app.include_router(cv_router)

Note:
    All routes are prefixed with /api/cv and tagged for OpenAPI docs.
    HTTP handling logic is in cv_controller.py, not here.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, Query, Request, status

from app.db.models.user import User
from app.features.auth.auth_dependencies import get_current_user
from app.core.rate_limit import limiter, auth_limiter, RATE_LIMIT_UPLOAD, RATE_LIMIT_DEFAULT, RATE_LIMIT_PUBLIC, get_ip_address

from .cv_controller import CVController
from .cv_schemas import (
    UploadResponse,
    ErrorResponse,
    SimilarCVsResponse,
    CVRankingResponse,
    CVCompareRequest,
    CVCompareResponse,
    CVSearchRequest,
    CVSearchResponse,
)
from .cv_dependencies import get_cv_service, get_similarity_service
from .cv_service import CVService
from .similarity_service import SimilarityService

# Router instance with prefix and OpenAPI tags
router = APIRouter(
    prefix="/api/cv",
    tags=["CV Screening"],
)

# Controller instance
controller = CVController()


# =============================================================================
# Route Definitions
# =============================================================================

@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or processing error"},
        401: {"description": "Not authenticated"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Upload and Evaluate CV",
    description="Upload a PDF/DOCX CV file and receive a structured evaluation based on hiring criteria.",
)
@limiter.limit(RATE_LIMIT_UPLOAD)
async def upload_and_evaluate_cv(
    request: Request,
    file: UploadFile = File(..., description="PDF or DOCX file containing the CV"),
    template_id: Optional[uuid.UUID] = Query(None, description="Optional evaluation template ID"),
    cv_service: CVService = Depends(get_cv_service),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    """Route handler for CV upload and evaluation."""
    return await controller.upload_and_evaluate(
        file=file,
        cv_service=cv_service,
        current_user=current_user,
        template_id=template_id,
    )


@router.get(
    "/",
    summary="List CVs",
    description="Get a paginated list of the current user's uploaded CVs.",
    responses={401: {"description": "Not authenticated"}},
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def list_cvs(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of CVs to return"),
    offset: int = Query(0, ge=0, description="Number of CVs to skip"),
    cv_service: CVService = Depends(get_cv_service),
    current_user: User = Depends(get_current_user),
):
    """Route handler for listing user's CVs."""
    return await controller.list_cvs(
        cv_service=cv_service,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{cv_id}",
    summary="Get CV Details",
    description="Get detailed information about a specific CV including evaluation results.",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "CV not found"},
    },
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_cv(
    request: Request,
    cv_id: uuid.UUID,
    cv_service: CVService = Depends(get_cv_service),
    current_user: User = Depends(get_current_user),
):
    """Route handler for getting CV details."""
    return await controller.get_cv(
        cv_id=cv_id,
        cv_service=cv_service,
        current_user=current_user,
    )


@router.delete(
    "/{cv_id}",
    summary="Delete CV",
    description="Delete a CV and all related data (evaluations, embeddings, chat history).",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "CV not found"},
    },
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def delete_cv(
    request: Request,
    cv_id: uuid.UUID,
    cv_service: CVService = Depends(get_cv_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Route handler for deleting a CV."""
    return await controller.delete_cv(
        cv_id=cv_id,
        cv_service=cv_service,
        current_user=current_user,
    )


@router.post(
    "/{cv_id}/re-evaluate",
    response_model=UploadResponse,
    summary="Re-evaluate CV",
    description="Re-evaluate an existing CV with a different evaluation template.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid template"},
        401: {"description": "Not authenticated"},
        404: {"description": "CV not found"},
    },
)
@limiter.limit(RATE_LIMIT_UPLOAD)
async def re_evaluate_cv(
    request: Request,
    cv_id: uuid.UUID,
    template_id: Optional[uuid.UUID] = Query(None, description="New evaluation template ID"),
    cv_service: CVService = Depends(get_cv_service),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    """Route handler for re-evaluating a CV."""
    return await controller.re_evaluate_cv(
        cv_id=cv_id,
        cv_service=cv_service,
        current_user=current_user,
        template_id=template_id,
    )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the CV screening service is operational.",
)
@auth_limiter.limit(RATE_LIMIT_PUBLIC)
async def health_check(
    request: Request,
    cv_service: CVService = Depends(get_cv_service),
) -> dict:
    """Route handler for health check."""
    return await controller.health_check(cv_service)


# =============================================================================
# Similarity Search Routes
# =============================================================================

@router.get(
    "/{cv_id}/similar",
    response_model=SimilarCVsResponse,
    summary="Find Similar CVs",
    description="""
    Find CVs similar to the given CV using vector embeddings.
    
    Uses cosine similarity on averaged chunk embeddings to find
    semantically similar candidates in your CV collection.
    
    **Parameters:**
    - `limit`: Maximum number of similar CVs to return (1-20)
    - `min_similarity`: Minimum similarity threshold (0-1)
    """,
    responses={
        400: {"model": ErrorResponse, "description": "CV has no embeddings"},
        401: {"description": "Not authenticated"},
        404: {"description": "CV not found"},
    },
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def find_similar_cvs(
    request: Request,
    cv_id: uuid.UUID,
    limit: int = Query(5, ge=1, le=20, description="Maximum results"),
    min_similarity: float = Query(0.3, ge=0, le=1, description="Minimum similarity (0-1)"),
    similarity_service: SimilarityService = Depends(get_similarity_service),
    current_user: User = Depends(get_current_user),
) -> SimilarCVsResponse:
    """Route handler for finding similar CVs."""
    return await controller.find_similar_cvs(
        cv_id=cv_id,
        similarity_service=similarity_service,
        current_user=current_user,
        limit=limit,
        min_similarity=min_similarity,
    )


@router.get(
    "/{cv_id}/ranking",
    response_model=CVRankingResponse,
    summary="Get CV Ranking",
    description="""
    Get percentile ranking for a CV among your uploaded CVs.
    
    Rankings are based on evaluation scores, not similarity.
    Returns the CV's rank, percentile, and comparison statistics.
    
    **Example Response:**
    - `percentile: 85` means the CV scored better than 85% of candidates
    - `rank: 3` means this is the 3rd best CV out of all
    - `label: "Top 10%"` provides a human-readable label
    """,
    responses={
        400: {"model": ErrorResponse, "description": "CV not evaluated"},
        401: {"description": "Not authenticated"},
        404: {"description": "CV not found"},
    },
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_cv_ranking(
    request: Request,
    cv_id: uuid.UUID,
    similarity_service: SimilarityService = Depends(get_similarity_service),
    current_user: User = Depends(get_current_user),
) -> CVRankingResponse:
    """Route handler for getting CV ranking."""
    return await controller.get_cv_ranking(
        cv_id=cv_id,
        similarity_service=similarity_service,
        current_user=current_user,
    )


@router.post(
    "/compare",
    response_model=CVCompareResponse,
    summary="Compare CVs",
    description="""
    Compare multiple CVs head-to-head.
    
    Returns:
    - Detailed info for each CV (scores, status)
    - Pairwise similarity matrix (NxN)
    - Best match (highest score)
    - Most similar pair
    
    **Limits:** 2-10 CVs per comparison.
    """,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid CV count or IDs"},
        401: {"description": "Not authenticated"},
        404: {"description": "CV not found"},
    },
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def compare_cvs(
    request: Request,
    data: CVCompareRequest,
    similarity_service: SimilarityService = Depends(get_similarity_service),
    current_user: User = Depends(get_current_user),
) -> CVCompareResponse:
    """Route handler for comparing CVs."""
    return await controller.compare_cvs(
        request=data,
        similarity_service=similarity_service,
        current_user=current_user,
    )


@router.post(
    "/search",
    response_model=CVSearchResponse,
    summary="Semantic CV Search",
    description="""
    Search CVs by natural language query.
    
    Converts your query to a vector embedding and finds CVs with
    similar content. Great for finding candidates with specific skills.
    
    **Example queries:**
    - "Python developer with fintech experience"
    - "React developer familiar with AI tools"
    - "Senior engineer with team lead experience"
    """,
    responses={
        401: {"description": "Not authenticated"},
    },
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def search_cvs(
    request: Request,
    data: CVSearchRequest,
    similarity_service: SimilarityService = Depends(get_similarity_service),
    current_user: User = Depends(get_current_user),
) -> CVSearchResponse:
    """Route handler for semantic CV search."""
    return await controller.search_cvs(
        request=data,
        similarity_service=similarity_service,
        current_user=current_user,
    )
