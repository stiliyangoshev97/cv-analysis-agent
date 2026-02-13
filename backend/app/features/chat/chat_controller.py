"""Chat controller for HTTP request handling.

This module provides the ChatController class for handling HTTP
requests related to RAG-powered CV chat. Controllers handle request
parsing, response formatting, and error handling.

Classes:
    ChatController: HTTP handlers for chat endpoints.

Example:
    Using the controller in routes::
    
        @router.post("/{cv_id}")
        async def ask_question(
            cv_id: UUID,
            request: ChatMessageRequest,
            current_user: User = Depends(get_current_user),
            chat_service: ChatService = Depends(get_chat_service),
        ):
            return await ChatController.ask_question(
                cv_id, request, current_user, chat_service
            )
"""

import uuid
from typing import List

from fastapi import HTTPException, status

from app.db.models.user import User
from .chat_service import ChatService
from .chat_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    ExplainCriterionRequest,
    ExplainCriterionResponse,
    CompareRequest,
    CompareResponse,
    AskResponse,
)


class ChatController:
    """Controller for chat HTTP endpoints.
    
    Handles request validation, calls ChatService, and formats responses.
    All methods are static as they don't maintain state.
    
    Example:
        >>> response = await ChatController.ask_question(
        ...     cv_id=cv_id,
        ...     request=ChatMessageRequest(message="What's their experience?"),
        ...     current_user=user,
        ...     chat_service=service,
        ... )
    """
    
    @staticmethod
    async def ask_question(
        cv_id: uuid.UUID,
        request: ChatMessageRequest,
        current_user: User,
        chat_service: ChatService,
    ) -> AskResponse:
        """Handle POST /api/chat/{cv_id} - Ask a question about a CV.
        
        Args:
            cv_id: CV UUID from path.
            request: Request body with question.
            current_user: Authenticated user.
            chat_service: Injected chat service.
        
        Returns:
            AskResponse with assistant message and metadata.
        
        Raises:
            HTTPException: 404 if CV not found, 403 if access denied.
        """
        try:
            result = await chat_service.ask(
                cv_id=cv_id,
                user_id=current_user.id,
                question=request.message,
            )
            
            return AskResponse(
                message=ChatMessageResponse(
                    id=result.message.id,
                    role=result.message.role,
                    content=result.message.message,
                    created_at=result.message.created_at,
                    sources=result.sources,
                ),
                sources_used=result.sources_count,
            )
        
        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message,
                )
            elif "access" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )
    
    @staticmethod
    async def get_history(
        cv_id: uuid.UUID,
        current_user: User,
        chat_service: ChatService,
        limit: int | None = None,
    ) -> ChatHistoryResponse:
        """Handle GET /api/chat/{cv_id} - Get chat history.
        
        Args:
            cv_id: CV UUID from path.
            current_user: Authenticated user.
            chat_service: Injected chat service.
            limit: Optional message limit query param.
        
        Returns:
            ChatHistoryResponse with all messages.
        
        Raises:
            HTTPException: 404 if CV not found, 403 if access denied.
        """
        try:
            messages = await chat_service.get_history(
                cv_id=cv_id,
                user_id=current_user.id,
                limit=limit,
            )
            
            return ChatHistoryResponse(
                cv_id=cv_id,
                messages=[
                    ChatMessageResponse(
                        id=msg.id,
                        role=msg.role,
                        content=msg.message,
                        created_at=msg.created_at,
                        sources=[],  # History doesn't include sources
                    )
                    for msg in messages
                ],
                total=len(messages),
            )
        
        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message,
                )
            elif "access" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )
    
    @staticmethod
    async def clear_history(
        cv_id: uuid.UUID,
        current_user: User,
        chat_service: ChatService,
    ) -> dict:
        """Handle DELETE /api/chat/{cv_id} - Clear chat history.
        
        Args:
            cv_id: CV UUID from path.
            current_user: Authenticated user.
            chat_service: Injected chat service.
        
        Returns:
            Dict with deleted count.
        
        Raises:
            HTTPException: 404 if CV not found, 403 if access denied.
        """
        try:
            count = await chat_service.clear_history(
                cv_id=cv_id,
                user_id=current_user.id,
            )
            
            return {
                "success": True,
                "message": f"Deleted {count} messages",
                "deleted_count": count,
            }
        
        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message,
                )
            elif "access" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )
    
    @staticmethod
    async def explain_criterion(
        cv_id: uuid.UUID,
        criterion: str,
        request: ExplainCriterionRequest,
        current_user: User,
        chat_service: ChatService,
    ) -> ExplainCriterionResponse:
        """Handle POST /api/chat/{cv_id}/explain/{criterion}.
        
        Generate a detailed explanation for why a criterion received
        a particular score.
        
        Args:
            cv_id: CV UUID from path.
            criterion: Criterion name from path.
            request: Optional request body.
            current_user: Authenticated user.
            chat_service: Injected chat service.
        
        Returns:
            ExplainCriterionResponse with detailed explanation.
        
        Raises:
            HTTPException: 404 if CV or criterion not found.
        """
        try:
            result = await chat_service.explain_criterion(
                cv_id=cv_id,
                user_id=current_user.id,
                criterion_name=criterion,
            )
            
            return ExplainCriterionResponse(
                criterion=result["criterion"],
                score=result["score"],
                max_score=result["max_score"],
                explanation=result["explanation"],
                evidence=result["evidence"] if request.include_cv_evidence else [],
            )
        
        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message,
                )
            elif "access" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )
    
    @staticmethod
    async def compare_cvs(
        request: CompareRequest,
        current_user: User,
        chat_service: ChatService,
    ) -> CompareResponse:
        """Handle POST /api/chat/compare - Compare multiple CVs.
        
        Generate a comparison analysis of 2-5 CVs.
        
        Args:
            request: Request body with CV IDs and question.
            current_user: Authenticated user.
            chat_service: Injected chat service.
        
        Returns:
            CompareResponse with comparison analysis.
        
        Raises:
            HTTPException: 404 if any CV not found.
        """
        try:
            result = await chat_service.compare_cvs(
                cv_ids=request.cv_ids,
                user_id=current_user.id,
                question=request.question,
            )
            
            return CompareResponse(
                cv_ids=result["cv_ids"],
                comparison=result["comparison"],
                ranking=result.get("ranking"),
            )
        
        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message,
                )
            elif "access" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )
