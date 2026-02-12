"""CV service for business logic orchestration.

This module contains the CVService class which handles the core
business logic for CV processing and evaluation. It orchestrates
calls to specialized services (PDF extraction, AI evaluation).

The service is responsible for:
- Coordinating PDF validation and text extraction
- Orchestrating AI-powered CV evaluation
- Building response objects

Classes:
    CVService: Main orchestration service for CV operations.

Example:
    Using the service::
    
        cv_service = CVService()
        result = await cv_service.process_cv(pdf_bytes, "resume.pdf")
        print(result.evaluation.match_score)

Note:
    This service orchestrates other services (PDFService, EvaluationService).
    Keep this layer focused on coordination, not implementation details.
"""

import logging
from typing import Optional

from .cv_schemas import UploadResponse, CVEvaluationResponse
from .services.pdf_service import PDFService
from .services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)


class CVService:
    """Orchestration service for CV processing operations.
    
    Coordinates the CV screening workflow by calling specialized
    services for PDF processing and AI evaluation.
    
    Attributes:
        pdf_service: Service for PDF text extraction.
        evaluation_service: Service for AI-powered evaluation.
    
    Methods:
        process_cv: Full CV processing pipeline (extract + evaluate).
        health_check: Check if all dependencies are operational.
    
    Example:
        >>> service = CVService()
        >>> result = await service.process_cv(pdf_bytes, "resume.pdf")
        >>> if result.success:
        ...     print(result.evaluation.status)
    """
    
    def __init__(self) -> None:
        """Initialize CV service with dependencies.
        
        Creates instances of specialized services for PDF processing
        and AI evaluation.
        """
        self.pdf_service = PDFService()
        self.evaluation_service = EvaluationService()
    
    async def process_cv(self, pdf_bytes: bytes, filename: str) -> UploadResponse:
        """Process a CV through the full screening pipeline.
        
        Validates the PDF, extracts text content, and evaluates
        the CV using AI.
        
        Args:
            pdf_bytes: Raw bytes of the uploaded PDF file.
            filename: Original filename for context and logging.
        
        Returns:
            UploadResponse containing:
                - success: Whether processing completed successfully
                - message: Status message
                - evaluation: CVEvaluationResponse with scores
        
        Raises:
            ValueError: If PDF is invalid or text extraction fails.
        
        Example:
            >>> with open("resume.pdf", "rb") as f:
            ...     pdf_bytes = f.read()
            >>> result = await service.process_cv(pdf_bytes, "resume.pdf")
            >>> print(result.evaluation.match_score)
        """
        logger.info(f"Starting CV processing: {filename}")
        
        # Step 1: Validate PDF
        is_valid, error_msg = self.pdf_service.validate_pdf(pdf_bytes)
        if not is_valid:
            logger.warning(f"Invalid PDF: {error_msg}")
            raise ValueError(error_msg)
        
        # Step 2: Extract text from PDF
        logger.debug(f"Extracting text from: {filename}")
        cv_text = self.pdf_service.extract_text_from_bytes(pdf_bytes)
        logger.info(f"Extracted {len(cv_text)} characters from {filename}")
        
        # Step 3: Evaluate CV using AI
        logger.debug(f"Evaluating CV: {filename}")
        evaluation = self.evaluation_service.evaluate_cv(cv_text, filename)
        logger.info(f"Evaluation complete: {filename} - Score: {evaluation.match_score}")
        
        # Step 4: Build response
        return UploadResponse(
            success=True,
            message="CV evaluated successfully",
            evaluation=evaluation
        )
    
    def health_check(self) -> bool:
        """Check if the CV service and dependencies are operational.
        
        Verifies that the AI evaluation service is properly configured.
        
        Returns:
            True if all dependencies are operational, False otherwise.
        
        Example:
            >>> service = CVService()
            >>> if service.health_check():
            ...     print("Service is ready")
        """
        return self.evaluation_service.health_check()
