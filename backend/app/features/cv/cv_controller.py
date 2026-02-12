"""CV controller for HTTP request handling.

This module contains the CVController class which handles HTTP-level
concerns for CV screening endpoints. It validates requests, calls
the service layer, and formats responses.

The controller is responsible for:
- Validating file uploads (type, size)
- Calling the CV service for processing
- Handling errors and converting them to HTTP responses
- Formatting successful responses

Classes:
    CVController: Handles all CV screening HTTP endpoints.

Example:
    Using the controller in routes::
    
        from .cv_controller import CVController
        
        controller = CVController()
        
        @router.post("/upload")
        async def upload(file: UploadFile, cv_service: CVService):
            return await controller.upload_and_evaluate(file, cv_service)

Note:
    Business logic should NOT be in this file. It belongs in cv_service.py.
    This controller only handles HTTP concerns.
"""

import logging
from fastapi import UploadFile, HTTPException, status

from .cv_schemas import UploadResponse
from .cv_service import CVService
from app.config import get_settings

logger = logging.getLogger(__name__)


class CVController:
    """Controller for CV screening HTTP endpoints.
    
    Handles HTTP request/response logic for CV operations.
    Delegates business logic to CVService.
    
    Methods:
        upload_and_evaluate: Handle CV upload and evaluation requests.
        health_check: Handle health check requests.
    
    Example:
        >>> controller = CVController()
        >>> response = await controller.upload_and_evaluate(file, cv_service)
    """
    
    async def upload_and_evaluate(
        self,
        file: UploadFile,
        cv_service: CVService
    ) -> UploadResponse:
        """Handle CV upload and evaluation request.
        
        Validates the uploaded file, extracts text, and evaluates
        the CV using AI.
        
        Args:
            file: Uploaded PDF file from the request.
            cv_service: Injected CV service instance.
        
        Returns:
            UploadResponse with success status and evaluation results.
        
        Raises:
            HTTPException: 400 if file is invalid or processing fails.
            HTTPException: 500 if unexpected error occurs.
        
        Example:
            POST /api/cv/upload
            Content-Type: multipart/form-data
            file: [PDF binary data]
        """
        settings = get_settings()
        
        # Validate filename
        if not file.filename:
            logger.warning("Upload attempt with no filename")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PDF files are accepted."
            )
        
        try:
            # Read file content
            content = await file.read()
            
            # Validate file size
            max_size_bytes = settings.max_file_size_mb * 1024 * 1024
            if len(content) > max_size_bytes:
                logger.warning(f"File too large: {len(content)} bytes")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB."
                )
            
            # Delegate to service for processing
            logger.info(f"Processing CV: {file.filename}")
            result = await cv_service.process_cv(content, file.filename)
            
            return result
            
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error processing CV: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while processing the CV"
            )
    
    async def health_check(self, cv_service: CVService) -> dict:
        """Handle health check request.
        
        Returns the operational status of the CV screening service.
        
        Args:
            cv_service: Injected CV service instance.
        
        Returns:
            Dict with service status information.
        
        Example:
            GET /api/cv/health
            Response: {"status": "healthy", "service": "CV Screening Agent", ...}
        """
        api_configured = cv_service.health_check()
        
        return {
            "status": "healthy" if api_configured else "degraded",
            "service": "CV Screening Agent",
            "ai_configured": api_configured
        }
