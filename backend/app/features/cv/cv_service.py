"""CV service for business logic orchestration.

This module contains the CVService class which handles the core
business logic for CV processing and evaluation. It orchestrates
LangChain components and repositories for document processing,
AI evaluation, and database persistence.

The service is responsible for:
- Processing PDF/DOCX uploads with LangChain DocumentProcessor
- Generating and storing embeddings via pgvector
- Evaluating CVs using LangChain EvaluationChain
- Persisting CVs, evaluations, and embeddings to the database
- Coordinating between repositories

Classes:
    CVService: Main orchestration service for CV operations.

Example:
    Using the service::
    
        async with get_db_session() as session:
            service = CVService(session)
            result = await service.process_and_evaluate(
                file_content=pdf_bytes,
                filename="resume.pdf",
                user_id=current_user.id
            )
            print(result.evaluation.percentage)

Note:
    This service requires a database session and orchestrates:
    - DocumentProcessor (LangChain) for PDF/DOCX loading
    - EvaluationChain (LangChain) for AI scoring
    - EmbeddingService (LangChain) for vector embeddings
    - CVRepository, EvaluationRepository, TemplateRepository, EmbeddingRepository
"""

import logging
import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cv import CV, CVStatus, CVEvaluation, EvaluationStatus
from app.langchain.document_processor import DocumentProcessor, ProcessedDocument
from app.langchain.chains.evaluation_chain import (
    EvaluationChain,
    CVEvaluationResult,
    get_evaluation_chain,
)
from app.langchain.embeddings import EmbeddingService
from app.langchain.config import get_llm, get_embeddings
from app.features.settings.user_keys_service import UserKeysService, UserAPIKeys
from app.agents.tools import extract_candidate_name

from .cv_repository import CVRepository
from .evaluation_repository import EvaluationRepository
from .template_repository import TemplateRepository
from .embedding_repository import EmbeddingRepository
from .cv_schemas import UploadResponse, CVEvaluationResponse, EvaluationCriteria, PassFailStatus
from .services.pdf_service import PDFService

from app.features.notification.notification_service import NotificationService
from app.features.notification.notification_schemas import CVNotificationData

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of CV processing and evaluation.
    
    Attributes:
        cv: The persisted CV entity.
        evaluation: The evaluation result from LangChain.
        db_evaluation: The persisted CVEvaluation entity.
        chunks_stored: Number of embedding chunks stored.
    """
    cv: CV
    evaluation: CVEvaluationResult
    db_evaluation: CVEvaluation
    chunks_stored: int


class CVService:
    """Orchestration service for CV processing operations.
    
    Integrates LangChain components with repositories for a complete
    CV processing pipeline: upload → extract → embed → evaluate → persist.
    
    Attributes:
        session: SQLAlchemy async session.
        cv_repo: Repository for CV operations.
        evaluation_repo: Repository for evaluation operations.
        template_repo: Repository for template operations.
        embedding_repo: Repository for embedding operations.
        document_processor: LangChain document processor.
        evaluation_chain: LangChain evaluation chain.
        embedding_service: LangChain embedding service.
        pdf_service: PDF validation service.
    
    Example:
        >>> async with get_db_session() as session:
        ...     service = CVService(session)
        ...     result = await service.process_and_evaluate(
        ...         file_content=pdf_bytes,
        ...         filename="resume.pdf",
        ...         user_id=user.id
        ...     )
        ...     print(f"Score: {result.evaluation.percentage}%")
    """
    
    def __init__(
        self,
        session: AsyncSession,
        evaluation_chain: Optional[EvaluationChain] = None,
        user_keys: Optional[UserAPIKeys] = None,
    ) -> None:
        """Initialize CV service with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
            evaluation_chain: Optional pre-configured evaluation chain.
            user_keys: Optional user API keys (fetched separately for each user).
        """
        self.session = session
        self.user_keys = user_keys
        
        # Initialize repositories
        self.cv_repo = CVRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
        self.template_repo = TemplateRepository(session)
        self.embedding_repo = EmbeddingRepository(session)
        
        # Initialize UserKeysService for fetching user keys
        self.user_keys_service = UserKeysService(session)
        
        # Initialize LangChain components (will be configured per-request with user keys)
        self.document_processor = DocumentProcessor()
        self._evaluation_chain = evaluation_chain  # May be overridden per-request
        
        # Legacy PDF service for validation
        self.pdf_service = PDFService()
    
    async def process_and_evaluate(
        self,
        file_content: bytes,
        filename: str,
        user_id: uuid.UUID,
        template_id: Optional[uuid.UUID] = None,
    ) -> ProcessingResult:
        """Process a CV through the full pipeline.
        
        1. Validate and extract text from PDF/DOCX
        2. Create CV record in database (status: PROCESSING)
        3. Generate and store embeddings in pgvector
        4. Evaluate CV using LangChain chain
        5. Store evaluation results
        6. Update CV status to EVALUATED
        
        Args:
            file_content: Raw bytes of the uploaded file.
            filename: Original filename (determines file type).
            user_id: UUID of the user uploading the CV.
            template_id: Optional template UUID (uses default if not provided).
        
        Returns:
            ProcessingResult with CV, evaluation, and metadata.
        
        Raises:
            ValueError: If file is invalid or unsupported.
            Exception: If evaluation fails (CV status set to ERROR).
        
        Example:
            >>> result = await service.process_and_evaluate(
            ...     file_content=pdf_bytes,
            ...     filename="john_doe_cv.pdf",
            ...     user_id=current_user.id
            ... )
            >>> print(f"Candidate: {result.cv.candidate_name}")
            >>> print(f"Score: {result.evaluation.percentage}%")
            >>> print(f"Passed: {result.evaluation.passed}")
        """
        logger.info(f"Starting CV processing: {filename} for user {user_id}")
        
        # Step 0: Get user's API keys (required for embeddings and evaluation)
        user_keys = await self.user_keys_service.validate_keys_for_cv_processing(user_id)
        logger.debug(f"Using LLM provider: {user_keys.default_provider}")
        
        # Create embedding service with user's OpenAI key
        embedding_service = EmbeddingService(
            session=self.session,
            api_key=user_keys.openai_key,
        )
        
        # Create evaluation chain with user's LLM key
        llm = get_llm(
            provider=user_keys.default_provider,
            api_key=user_keys.get_llm_key(),
        )
        evaluation_chain = self._evaluation_chain or EvaluationChain(llm=llm)
        
        # Step 1: Validate file (for PDFs)
        if filename.lower().endswith('.pdf'):
            is_valid, error_msg = self.pdf_service.validate_pdf(file_content)
            if not is_valid:
                logger.warning(f"Invalid PDF: {error_msg}")
                raise ValueError(error_msg)
        
        # Step 2: Process document with LangChain
        logger.debug(f"Processing document: {filename}")
        processed = await self.document_processor.process_upload(file_content, filename)
        logger.info(f"Extracted {len(processed.full_text)} chars, {processed.chunk_count} chunks")
        
        # Step 2.5: Extract candidate name from CV text
        candidate_name = extract_candidate_name(processed.full_text)
        logger.debug(f"Extracted candidate name: {candidate_name}")
        
        # Step 3: Create CV record in database
        cv = CV(
            user_id=user_id,
            filename=filename,
            original_text=processed.full_text,
            candidate_name=candidate_name,
            status=CVStatus.PROCESSING.value,
        )
        cv = await self.cv_repo.create(cv)
        logger.debug(f"Created CV record: {cv.id}")
        
        try:
            # Step 4: Generate and store embeddings (using user's OpenAI key)
            logger.debug(f"Generating embeddings for {processed.chunk_count} chunks")
            embeddings = await embedding_service.store_cv_embeddings(
                cv_id=cv.id,
                chunks=processed.chunks,
            )
            chunks_stored = len(embeddings)
            logger.info(f"Stored {chunks_stored} embeddings for CV {cv.id}")
            
            # Step 5: Get evaluation template
            template = None
            criteria_list = []
            
            if template_id:
                template = await self.template_repo.get_with_criteria(template_id)
            
            if not template:
                # Use default system template
                template = await self.template_repo.get_default_template()
            
            if template:
                criteria_list = template.criteria
                logger.debug(f"Using template: {template.name} with {len(criteria_list)} criteria")
            else:
                logger.warning("No evaluation template found, using hardcoded criteria")
                # Fallback to hardcoded criteria (shouldn't happen if seed data exists)
                raise ValueError("No evaluation template available. Please run seed data.")
            
            # Step 6: Evaluate CV using LangChain (using user's LLM key)
            logger.debug(f"Evaluating CV with template: {template.name}")
            evaluation = await evaluation_chain.evaluate_with_template(
                cv_text=processed.full_text,
                template=template,
                criteria_list=criteria_list,
            )
            logger.info(f"Evaluation complete: {evaluation.percentage}%, passed={evaluation.passed}")
            
            # Step 7: Store evaluation results
            status = EvaluationStatus.PASS if evaluation.passed else EvaluationStatus.FAIL
            
            # Build criteria results JSON
            criteria_results = {
                score.name: {
                    "score": score.score,
                    "max_score": score.max_score,
                    "reasoning": score.reasoning,
                    "evidence": score.evidence,
                }
                for score in evaluation.criteria_scores
            }
            
            db_evaluation = CVEvaluation(
                cv_id=cv.id,
                template_id=template.id,
                score=int(evaluation.percentage),
                status=status.value,
                reasoning=evaluation.summary,
                criteria_results=criteria_results,
            )
            db_evaluation = await self.evaluation_repo.create(db_evaluation)
            logger.debug(f"Stored evaluation: {db_evaluation.id}")
            
            # Step 8: Update CV status and extract candidate name
            # (Could enhance this with a dedicated name extraction step)
            cv.status = CVStatus.EVALUATED.value
            cv = await self.cv_repo.update(cv)
            
            await self.session.commit()
            logger.info(f"CV processing complete: {cv.id}")
            
            # Step 9: Trigger notifications if threshold met (non-blocking)
            try:
                await self._trigger_notifications_if_applicable(
                    user_id=user_id,
                    cv=cv,
                    evaluation=evaluation,
                )
            except Exception as notif_error:
                # Don't fail the upload if notification fails
                logger.warning(f"Notification failed (non-blocking): {notif_error}")
            
            return ProcessingResult(
                cv=cv,
                evaluation=evaluation,
                db_evaluation=db_evaluation,
                chunks_stored=chunks_stored,
            )
            
        except Exception as e:
            # Mark CV as error status
            logger.error(f"CV processing failed: {e}")
            cv.status = CVStatus.ERROR.value
            await self.cv_repo.update(cv)
            await self.session.commit()
            raise
    
    async def get_cv(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        include_evaluation: bool = True,
    ) -> Optional[CV]:
        """Get a CV by ID, ensuring user ownership.
        
        Args:
            cv_id: UUID of the CV.
            user_id: UUID of the requesting user.
            include_evaluation: Whether to load evaluations.
        
        Returns:
            CV if found and owned by user, None otherwise.
        """
        cv = await self.cv_repo.get_by_id(cv_id, include_evaluations=include_evaluation)
        
        if cv and cv.user_id == user_id:
            return cv
        return None
    
    async def list_user_cvs(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[CV], int]:
        """List CVs for a user with pagination.
        
        Args:
            user_id: UUID of the user.
            limit: Maximum number of CVs to return.
            offset: Number of CVs to skip.
        
        Returns:
            Tuple of (CVs list, total count).
        """
        cvs = await self.cv_repo.get_by_user(
            user_id=user_id,
            include_evaluations=True,
            limit=limit,
            offset=offset,
        )
        total = await self.cv_repo.count_by_user(user_id)
        return cvs, total
    
    async def delete_cv(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a CV and all related data.
        
        Cascades to delete evaluations, embeddings, and chat history.
        
        Args:
            cv_id: UUID of the CV to delete.
            user_id: UUID of the requesting user.
        
        Returns:
            True if deleted, False if not found or not owned.
        """
        cv = await self.cv_repo.get_by_id(cv_id)
        
        if not cv or cv.user_id != user_id:
            return False
        
        await self.cv_repo.delete(cv)
        await self.session.commit()
        logger.info(f"Deleted CV {cv_id} and related data")
        return True
    
    async def re_evaluate(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        template_id: Optional[uuid.UUID] = None,
    ) -> Optional[ProcessingResult]:
        """Re-evaluate an existing CV with a different template.
        
        Useful for comparing candidates against different criteria.
        
        Args:
            cv_id: UUID of the CV to re-evaluate.
            user_id: UUID of the requesting user.
            template_id: Optional new template to use.
        
        Returns:
            ProcessingResult if successful, None if CV not found.
        """
        cv = await self.cv_repo.get_by_id(cv_id)
        
        if not cv or cv.user_id != user_id:
            return None
        
        # Get user's API keys (required for evaluation)
        user_keys = await self.user_keys_service.validate_keys_for_cv_processing(user_id)
        logger.debug(f"Re-evaluating with LLM provider: {user_keys.default_provider}")
        
        # Create evaluation chain with user's LLM key
        llm = get_llm(
            provider=user_keys.default_provider,
            api_key=user_keys.get_llm_key(),
        )
        evaluation_chain = self._evaluation_chain or EvaluationChain(llm=llm)
        
        # Get template
        template = None
        if template_id:
            template = await self.template_repo.get_with_criteria(template_id)
        if not template:
            template = await self.template_repo.get_default_template()
        
        if not template:
            raise ValueError("No evaluation template available")
        
        # Re-evaluate using stored text
        evaluation = await evaluation_chain.evaluate_with_template(
            cv_text=cv.original_text,
            template=template,
            criteria_list=template.criteria,
        )
        
        # Store new evaluation
        status = EvaluationStatus.PASS if evaluation.passed else EvaluationStatus.FAIL
        criteria_results = {
            score.name: {
                "score": score.score,
                "max_score": score.max_score,
                "reasoning": score.reasoning,
                "evidence": score.evidence,
            }
            for score in evaluation.criteria_scores
        }
        
        db_evaluation = CVEvaluation(
            cv_id=cv.id,
            template_id=template.id,
            score=int(evaluation.percentage),
            status=status.value,
            reasoning=evaluation.summary,
            criteria_results=criteria_results,
        )
        db_evaluation = await self.evaluation_repo.create(db_evaluation)
        await self.session.commit()
        
        # Get embedding count
        chunks_stored = await self.embedding_repo.count_by_cv(cv_id)
        
        return ProcessingResult(
            cv=cv,
            evaluation=evaluation,
            db_evaluation=db_evaluation,
            chunks_stored=chunks_stored,
        )
    
    def convert_to_response(
        self,
        result: ProcessingResult,
    ) -> UploadResponse:
        """Convert ProcessingResult to API response schema.
        
        Translates LangChain evaluation result to the frontend schema.
        
        Args:
            result: ProcessingResult from process_and_evaluate.
        
        Returns:
            UploadResponse for API response.
        """
        # Convert LangChain criteria to API schema
        criteria = [
            EvaluationCriteria(
                name=score.name,
                passed=score.score >= (score.max_score * 0.5),  # Passed if >= 50% of max
                details=score.reasoning,
            )
            for score in result.evaluation.criteria_scores
        ]
        
        evaluation_response = CVEvaluationResponse(
            status=PassFailStatus.PASS if result.evaluation.passed else PassFailStatus.FAIL,
            match_score=int(result.evaluation.percentage),
            reasoning=result.evaluation.summary,
            criteria=criteria,
            candidate_name=result.cv.candidate_name,
        )
        
        return UploadResponse(
            success=True,
            message="CV evaluated successfully",
            cv_id=str(result.cv.id),
            evaluation=evaluation_response,
        )
    
    def health_check(self) -> bool:
        """Check if the CV service dependencies are operational.
        
        Returns:
            True if LangChain components are configured.
        """
        try:
            # Check if we can get the evaluation chain
            chain = get_evaluation_chain()
            return chain is not None
        except Exception:
            return False
    
    async def _trigger_notifications_if_applicable(
        self,
        user_id: uuid.UUID,
        cv: CV,
        evaluation: CVEvaluationResult,
    ) -> None:
        """Trigger notifications if CV score meets user's threshold.
        
        This method is called after CV evaluation to automatically
        dispatch notifications to enabled channels (email, WhatsApp).
        
        Args:
            user_id: UUID of the user who uploaded the CV.
            cv: The processed CV entity.
            evaluation: The evaluation result from LangChain.
        """
        try:
            notification_service = NotificationService(self.session)
            
            # Build notification data from CV and evaluation
            cv_notification_data = CVNotificationData(
                cv_id=str(cv.id),
                filename=cv.filename,
                candidate_name=cv.candidate_name,
                score=int(evaluation.percentage),
                passed=evaluation.passed,
                summary=evaluation.summary,
            )
            
            # Dispatch notification (checks threshold internally)
            result = await notification_service.dispatch_cv_notification(
                user_id=user_id,
                cv_data=cv_notification_data,
            )
            
            if result.should_notify:
                if result.success:
                    logger.info(
                        f"Notification dispatched for CV {cv.id}: "
                        f"email={result.email_sent}, whatsapp={result.whatsapp_sent}"
                    )
                elif result.channels_attempted:
                    logger.warning(
                        f"Notification attempted but failed for CV {cv.id}: "
                        f"{result.errors}"
                    )
                
                # Commit notification history entries
                await self.session.commit()
            else:
                logger.debug(
                    f"Score {evaluation.percentage}% below threshold "
                    f"{result.threshold}%, no notification sent"
                )
                
        except Exception as e:
            # Log but don't fail - notifications are non-critical
            logger.error(f"Error triggering notification for CV {cv.id}: {e}")
