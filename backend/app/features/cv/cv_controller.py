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

from .cv_schemas import (
    UploadResponse,
    CVListResponse,
    CVDetailResponse,
    SimilarCVsResponse,
    SimilarCVResponse,
    CVRankingResponse,
    CVCompareRequest,
    CVCompareResponse,
    CVComparisonItemResponse,
    CVSearchRequest,
    CVSearchResponse,
)
from .cv_service import CVService
from .similarity_service import SimilarityService

logger = logging.getLogger(__name__)

# =============================================================================
# File Validation Constants
# =============================================================================

# Allowed file extensions for CV uploads
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}

# Allowed MIME types for CV uploads
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/msword",  # .doc
    # Some systems may report these alternative types
    "application/x-pdf",
}

# Dangerous file extensions that should NEVER be allowed (security blocklist)
BLOCKED_EXTENSIONS = {
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff",
    # Executables
    ".exe", ".bat", ".cmd", ".sh", ".ps1", ".msi", ".dll", ".so",
    # Scripts
    ".js", ".py", ".rb", ".php", ".pl", ".vbs", ".jar", ".class",
    # Archives
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
    # Other dangerous
    ".html", ".htm", ".xml", ".json", ".csv", ".txt",
}


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
    
    def _validate_file_magic(self, content: bytes, extension: str) -> bool:
        """Validate file content against expected magic bytes.
        
        This provides defense-in-depth by checking actual file content,
        not just the extension which can be easily spoofed.
        
        Args:
            content: Raw file bytes.
            extension: File extension (e.g., '.pdf').
        
        Returns:
            True if file content matches expected format, False otherwise.
        """
        if len(content) < 8:
            return False
        
        if extension == ".pdf":
            # PDF files start with '%PDF-'
            return content[:5] == b'%PDF-'
        
        elif extension in (".docx", ".doc"):
            # DOCX files are ZIP archives (start with PK)
            # DOC files start with MS Office compound document signature
            docx_signature = content[:4] == b'PK\x03\x04'  # ZIP format
            doc_signature = content[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'  # OLE compound
            return docx_signature or doc_signature
        
        return False
    
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
        
        filename_lower = file.filename.lower()
        
        # Get file extension
        extension = ""
        if "." in filename_lower:
            extension = "." + filename_lower.rsplit(".", 1)[-1]
        
        # SECURITY: Check against blocklist first (defense in depth)
        if extension in BLOCKED_EXTENSIONS:
            logger.warning(f"Blocked file type attempt: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This file type is not allowed. Please upload PDF or DOCX files only."
            )
        
        # Validate file extension
        if extension not in ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file extension: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Accepted formats: PDF, DOCX"
            )
        
        # Validate MIME type (if provided by client)
        if file.content_type:
            # Allow some flexibility - browsers may not always send correct MIME type
            # But block obviously wrong types
            if file.content_type.startswith(("image/", "video/", "audio/", "text/html")):
                logger.warning(f"Blocked MIME type: {file.content_type} for {file.filename}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Please upload PDF or DOCX files only."
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
            
            # SECURITY: Validate magic bytes (file signature)
            if not self._validate_file_magic(content, extension):
                logger.warning(f"File magic bytes mismatch for: {file.filename}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file content. The file does not appear to be a valid PDF or DOCX."
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
    
    # =========================================================================
    # Similarity Search Methods
    # =========================================================================
    
    async def find_similar_cvs(
        self,
        cv_id: uuid.UUID,
        similarity_service: SimilarityService,
        current_user: User,
        limit: int = 5,
        min_similarity: float = 0.0,
    ) -> SimilarCVsResponse:
        """Handle find similar CVs request.
        
        Finds CVs similar to the given CV using vector embeddings.
        
        Args:
            cv_id: Source CV UUID.
            similarity_service: Injected similarity service.
            current_user: Authenticated user.
            limit: Maximum results to return.
            min_similarity: Minimum similarity threshold.
            
        Returns:
            SimilarCVsResponse with similar CVs.
            
        Raises:
            HTTPException: 404 if CV not found, 400 if no embeddings.
        """
        try:
            results = await similarity_service.find_similar_cvs(
                cv_id=cv_id,
                user_id=current_user.id,
                limit=limit,
                min_similarity=min_similarity,
            )
            
            return SimilarCVsResponse(
                source_cv_id=str(cv_id),
                similar_cvs=[
                    SimilarCVResponse(
                        cv_id=str(r.cv_id),
                        filename=r.filename,
                        candidate_name=r.candidate_name,
                        similarity_score=r.similarity_score,
                        evaluation_score=r.evaluation_score,
                        status=r.status,
                    )
                    for r in results
                ],
                total=len(results),
            )
            
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    
    async def get_cv_ranking(
        self,
        cv_id: uuid.UUID,
        similarity_service: SimilarityService,
        current_user: User,
    ) -> CVRankingResponse:
        """Handle CV ranking request.
        
        Returns percentile ranking for a CV among user's CVs.
        
        Args:
            cv_id: CV UUID to rank.
            similarity_service: Injected similarity service.
            current_user: Authenticated user.
            
        Returns:
            CVRankingResponse with percentile and rank info.
            
        Raises:
            HTTPException: 404 if CV not found, 400 if not evaluated.
        """
        try:
            ranking = await similarity_service.get_cv_ranking(
                cv_id=cv_id,
                user_id=current_user.id,
            )
            
            # Generate human-readable label
            if ranking.percentile >= 90:
                label = "Top 10%"
            elif ranking.percentile >= 75:
                label = "Top 25%"
            elif ranking.percentile >= 50:
                label = "Above Average"
            elif ranking.percentile >= 25:
                label = "Below Average"
            else:
                label = "Bottom 25%"
            
            return CVRankingResponse(
                cv_id=str(cv_id),
                percentile=ranking.percentile,
                rank=ranking.rank,
                total_cvs=ranking.total_cvs,
                evaluation_score=ranking.evaluation_score,
                average_score=ranking.average_score,
                highest_score=ranking.highest_score,
                label=label,
            )
            
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    
    async def compare_cvs(
        self,
        request: CVCompareRequest,
        similarity_service: SimilarityService,
        current_user: User,
    ) -> CVCompareResponse:
        """Handle CV comparison request.
        
        Compares multiple CVs head-to-head with similarity matrix.
        
        Args:
            request: Request with CV IDs to compare.
            similarity_service: Injected similarity service.
            current_user: Authenticated user.
            
        Returns:
            CVCompareResponse with comparison details.
            
        Raises:
            HTTPException: 400 for validation errors, 404 if CV not found.
        """
        try:
            cv_ids = [uuid.UUID(cid) for cid in request.cv_ids]
            
            comparison = await similarity_service.compare_cvs(
                cv_ids=cv_ids,
                user_id=current_user.id,
            )
            
            # Format most similar pair
            most_similar = None
            if comparison.most_similar_pair:
                cv1, cv2, sim = comparison.most_similar_pair
                most_similar = {
                    "cv_id_1": str(cv1),
                    "cv_id_2": str(cv2),
                    "similarity": sim,
                }
            
            return CVCompareResponse(
                cvs=[
                    CVComparisonItemResponse(
                        cv_id=str(item.cv_id),
                        filename=item.filename,
                        candidate_name=item.candidate_name,
                        evaluation_score=item.evaluation_score,
                        status=item.status,
                        similarity_to_first=item.similarity_to_first,
                    )
                    for item in comparison.cvs
                ],
                similarity_matrix=comparison.similarity_matrix,
                best_match_id=str(comparison.best_match_id) if comparison.best_match_id else None,
                most_similar_pair=most_similar,
            )
            
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    
    async def search_cvs(
        self,
        request: CVSearchRequest,
        similarity_service: SimilarityService,
        current_user: User,
    ) -> CVSearchResponse:
        """Handle semantic CV search request.
        
        Searches CVs by natural language query using embeddings.
        
        Args:
            request: Request with search query.
            similarity_service: Injected similarity service.
            current_user: Authenticated user.
            
        Returns:
            CVSearchResponse with matching CVs.
        """
        results = await similarity_service.search_by_query(
            query=request.query,
            user_id=current_user.id,
            limit=request.limit,
            min_similarity=request.min_similarity,
        )
        
        return CVSearchResponse(
            query=request.query,
            results=[
                SimilarCVResponse(
                    cv_id=str(r.cv_id),
                    filename=r.filename,
                    candidate_name=r.candidate_name,
                    similarity_score=r.similarity_score,
                    evaluation_score=r.evaluation_score,
                    status=r.status,
                )
                for r in results
            ],
            total=len(results),
        )
