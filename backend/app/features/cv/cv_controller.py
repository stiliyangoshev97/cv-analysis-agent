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
        async def upload(file: UploadFile, cv_service: CVService, user: User):
            return await controller.upload_and_evaluate(file, cv_service, user)

Note:
    Business logic should NOT be in this file. It belongs in cv_service.py.
    This controller only handles HTTP concerns.
"""

import logging
import uuid
from typing import Optional

from fastapi import UploadFile, HTTPException, status

from app.config import get_settings
from app.db.models.user import User

from .cv_schemas import UploadResponse, CVListResponse, CVDetailResponse
from .cv_service import CVService

logger = logging.getLogger(__name__)


class CVController:
    """Controller for CV screening HTTP endpoints.
    
    Handles HTTP request/response logic for CV operations.
    Delegates business logic to CVService.
    
    Methods:
        upload_and_evaluate: Handle CV upload and evaluation requests.
        list_cvs: Handle CV listing requests.
        get_cv: Handle single CV retrieval.
        delete_cv: Handle CV deletion.
        health_check: Handle health check requests.
    
    Example:
        >>> controller = CVController()
        >>> response = await controller.upload_and_evaluate(file, cv_service, user)
    """
    
    async def upload_and_evaluate(
        self,
        file: UploadFile,
        cv_service: CVService,
        current_user: User,
        template_id: Optional[uuid.UUID] = None,
    ) -> UploadResponse:
        """Handle CV upload and evaluation request.
        
        Validates the uploaded file, processes it with LangChain,
        stores embeddings, evaluates, and persists to database.
        
        Args:
            file: Uploaded PDF/DOCX file from the request.
            cv_service: Injected CV service instance.
            current_user: Authenticated user making the request.
            template_id: Optional evaluation template to use.
        
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
        
        # Validate file type (now supports PDF and DOCX)
        valid_extensions = (".pdf", ".docx", ".doc")
        if not file.filename.lower().endswith(valid_extensions):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Accepted formats: PDF, DOCX"
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
            
            # Process CV with LangChain integration
            logger.info(f"Processing CV: {file.filename} for user {current_user.id}")
            result = await cv_service.process_and_evaluate(
                file_content=content,
                filename=file.filename,
                user_id=current_user.id,
                template_id=template_id,
            )
            
            # Convert to API response
            return cv_service.convert_to_response(result)
            
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error processing CV: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while processing the CV"
            )
    
    async def list_cvs(
        self,
        cv_service: CVService,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> CVListResponse:
        """Handle CV listing request.
        
        Returns paginated list of user's CVs with evaluations.
        
        Args:
            cv_service: Injected CV service instance.
            current_user: Authenticated user making the request.
            limit: Maximum number of CVs to return.
            offset: Number of CVs to skip.
        
        Returns:
            CVListResponse with CVs and pagination info.
        """
        cvs, total = await cv_service.list_user_cvs(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
        
        return CVListResponse(
            cvs=[self._cv_to_summary(cv) for cv in cvs],
            total=total,
            limit=limit,
            offset=offset,
        )
    
    async def get_cv(
        self,
        cv_id: uuid.UUID,
        cv_service: CVService,
        current_user: User,
    ) -> CVDetailResponse:
        """Handle single CV retrieval.
        
        Args:
            cv_id: UUID of the CV to retrieve.
            cv_service: Injected CV service instance.
            current_user: Authenticated user making the request.
        
        Returns:
            CVDetailResponse with full CV and evaluation details.
        
        Raises:
            HTTPException: 404 if CV not found or not owned by user.
        """
        cv = await cv_service.get_cv(
            cv_id=cv_id,
            user_id=current_user.id,
        )
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return self._cv_to_detail(cv)
    
    async def delete_cv(
        self,
        cv_id: uuid.UUID,
        cv_service: CVService,
        current_user: User,
    ) -> dict:
        """Handle CV deletion request.
        
        Deletes CV and all related data (evaluations, embeddings, chat).
        
        Args:
            cv_id: UUID of the CV to delete.
            cv_service: Injected CV service instance.
            current_user: Authenticated user making the request.
        
        Returns:
            Success message dict.
        
        Raises:
            HTTPException: 404 if CV not found or not owned by user.
        """
        deleted = await cv_service.delete_cv(
            cv_id=cv_id,
            user_id=current_user.id,
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return {"message": "CV deleted successfully"}
    
    async def re_evaluate_cv(
        self,
        cv_id: uuid.UUID,
        cv_service: CVService,
        current_user: User,
        template_id: Optional[uuid.UUID] = None,
    ) -> UploadResponse:
        """Handle CV re-evaluation request.
        
        Re-evaluates an existing CV with a different template.
        
        Args:
            cv_id: UUID of the CV to re-evaluate.
            cv_service: Injected CV service instance.
            current_user: Authenticated user making the request.
            template_id: Optional new template to use.
        
        Returns:
            UploadResponse with new evaluation results.
        
        Raises:
            HTTPException: 404 if CV not found.
        """
        try:
            result = await cv_service.re_evaluate(
                cv_id=cv_id,
                user_id=current_user.id,
                template_id=template_id,
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="CV not found"
                )
            
            return cv_service.convert_to_response(result)
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
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
            "langchain_configured": api_configured,
            "features": {
                "pdf_processing": True,
                "docx_processing": True,
                "ai_evaluation": api_configured,
                "embedding_storage": api_configured,
            }
        }
    
    def _cv_to_summary(self, cv) -> dict:
        """Convert CV entity to summary dict."""
        latest_eval = cv.evaluations[0] if cv.evaluations else None
        
        return {
            "id": str(cv.id),
            "filename": cv.filename,
            "candidate_name": cv.candidate_name,
            "status": cv.status,
            "uploaded_at": cv.uploaded_at.isoformat(),
            "score": latest_eval.score if latest_eval else None,
            "evaluation_status": latest_eval.status if latest_eval else None,
        }
    
    def _cv_to_detail(self, cv) -> dict:
        """Convert CV entity to detailed dict."""
        latest_eval = cv.evaluations[0] if cv.evaluations else None
        
        return {
            "id": str(cv.id),
            "filename": cv.filename,
            "candidate_name": cv.candidate_name,
            "status": cv.status,
            "uploaded_at": cv.uploaded_at.isoformat(),
            "original_text": cv.original_text,
            "evaluation": {
                "id": str(latest_eval.id),
                "score": latest_eval.score,
                "status": latest_eval.status,
                "reasoning": latest_eval.reasoning,
                "criteria_results": latest_eval.criteria_results,
                "evaluated_at": latest_eval.evaluated_at.isoformat(),
            } if latest_eval else None,
        }
