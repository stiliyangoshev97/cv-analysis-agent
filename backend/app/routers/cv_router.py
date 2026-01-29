"""
CV Upload and Evaluation Router.
Handles the main API endpoints for CV screening.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..models.schemas import UploadResponse, ErrorResponse, CVEvaluationResponse
from ..services.pdf_service import PDFService
from ..services.evaluation_service import EvaluationService
from ..config import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cv", tags=["CV Screening"])


def get_evaluation_service() -> EvaluationService:
    """Dependency injection for evaluation service."""
    return EvaluationService()


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or processing error"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Upload and Evaluate CV",
    description="Upload a PDF CV file and receive a structured evaluation based on XBO.com hiring criteria."
)
async def upload_and_evaluate_cv(
    file: UploadFile = File(..., description="PDF file containing the CV"),
    settings: Settings = Depends(get_settings),
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> UploadResponse:
    """
    Upload a PDF CV and get an AI-powered evaluation.
    
    The evaluation checks for:
    - Education (High School Diploma or higher)
    - Fintech Experience (Finance/Crypto background)
    - Technical Skills (TypeScript/Python proficiency)
    
    Returns a structured scorecard with pass/fail status and detailed reasoning.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only PDF files are accepted."
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if len(content) > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB."
            )
        
        # Validate PDF
        is_valid, error_msg = PDFService.validate_pdf(content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract text from PDF
        logger.info(f"Processing CV: {file.filename}")
        cv_text = PDFService.extract_text_from_bytes(content)
        
        # Evaluate CV using AI
        evaluation = evaluation_service.evaluate_cv(cv_text, file.filename)
        
        return UploadResponse(
            success=True,
            message="CV evaluated successfully",
            evaluation=evaluation
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing CV: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while processing the CV"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the CV screening service is operational."
)
async def health_check(
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> dict:
    """
    Health check endpoint to verify service status.
    """
    api_configured = evaluation_service.health_check()
    
    return {
        "status": "healthy" if api_configured else "degraded",
        "service": "CV Screening Agent",
        "ai_configured": api_configured
    }
