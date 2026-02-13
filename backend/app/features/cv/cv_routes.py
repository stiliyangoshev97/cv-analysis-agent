"""CV routes configuration.

This module defines the FastAPI router for CV screening endpoints.
Routes are thin - they only wire up URL paths to controller handlers.

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

from fastapi import APIRouter, UploadFile, File, Depends, Query, status

from app.db.models.user import User
from app.features.auth.auth_dependencies import get_current_user

from .cv_controller import CVController
from .cv_schemas import UploadResponse, ErrorResponse
from .cv_dependencies import get_cv_service
from .cv_service import CVService

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
async def upload_and_evaluate_cv(
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
async def list_cvs(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of CVs to return"),
    offset: int = Query(0, ge=0, description="Number of CVs to skip"),
    cv_service: CVService = Depends(get_cv_service),
    current_user: User = Depends(get_current_user),
) -> dict:
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
async def get_cv(
    cv_id: uuid.UUID,
    cv_service: CVService = Depends(get_cv_service),
    current_user: User = Depends(get_current_user),
) -> dict:
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
async def delete_cv(
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
async def re_evaluate_cv(
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
async def health_check(
    cv_service: CVService = Depends(get_cv_service),
) -> dict:
    """Route handler for health check."""
    return await controller.health_check(cv_service)
