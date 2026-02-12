"""CV routes configuration.

This module defines the FastAPI router for CV screening endpoints.
Routes are thin - they only wire up URL paths to controller handlers.

Routes:
    POST /api/cv/upload - Upload and evaluate a CV
    GET /api/cv/health - Health check for CV service

Example:
    Including the router in the FastAPI app::
    
        from app.features.cv import cv_router
        app.include_router(cv_router)

Note:
    All routes are prefixed with /api/cv and tagged for OpenAPI docs.
    HTTP handling logic is in cv_controller.py, not here.
"""

from fastapi import APIRouter, UploadFile, File, Depends, status

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
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Upload and Evaluate CV",
    description="Upload a PDF CV file and receive a structured evaluation based on hiring criteria.",
)
async def upload_and_evaluate_cv(
    file: UploadFile = File(..., description="PDF file containing the CV"),
    cv_service: CVService = Depends(get_cv_service)
) -> UploadResponse:
    """Route handler for CV upload and evaluation."""
    return await controller.upload_and_evaluate(file, cv_service)


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the CV screening service is operational.",
)
async def health_check(
    cv_service: CVService = Depends(get_cv_service)
) -> dict:
    """Route handler for health check."""
    return await controller.health_check(cv_service)
