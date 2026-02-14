"""Chat feature route definitions.

This module defines the FastAPI routes for RAG-powered CV chat.
Routes are thin - they only wire dependencies and delegate to controllers.

Rate Limits:
    - All chat endpoints: 30/minute (LLM API costs)

Routes:
    POST   /api/chat/compare                  - Compare multiple CVs
    POST   /api/chat/{cv_id}                  - Ask question about CV
    GET    /api/chat/{cv_id}                  - Get chat history
    DELETE /api/chat/{cv_id}                  - Clear chat history
    POST   /api/chat/{cv_id}/explain/{criterion} - Explain criterion score

Note: /compare route must come BEFORE /{cv_id} routes due to FastAPI route ordering.

Example:
    The router is registered in main.py::
    
        from app.features.chat import chat_router
        app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from app.db.models.user import User
from app.features.auth.auth_dependencies import get_current_user
from app.core.rate_limit import limiter, RATE_LIMIT_CHAT, RATE_LIMIT_DEFAULT
from .chat_controller import ChatController
from .chat_dependencies import get_chat_service
from .chat_service import ChatService
from .chat_schemas import (
    ChatMessageRequest,
    ChatHistoryResponse,
    ExplainCriterionRequest,
    ExplainCriterionResponse,
    CompareRequest,
    CompareResponse,
    AskResponse,
)


router = APIRouter()


# =============================================================================
# Static routes MUST come before parameterized routes
# =============================================================================

@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="Compare multiple CVs",
    description="""
    Compare 2-5 CVs against each other.
    
    Useful for recruiters deciding between candidates.
    
    **Features:**
    - Side-by-side comparison
    - Highlights key differences
    - Optional ranking with justification
    
    **Example questions:**
    - "Compare their fintech experience"
    - "Who has better technical skills?"
    - "Compare overall fit for a senior role"
    """,
)
@limiter.limit(RATE_LIMIT_CHAT)
async def compare_cvs(
    request: Request,
    data: CompareRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> CompareResponse:
    """Compare multiple CVs."""
    return await ChatController.compare_cvs(
        request=data,
        current_user=current_user,
        chat_service=chat_service,
    )


# =============================================================================
# Parameterized routes (with {cv_id})
# =============================================================================

@router.post(
    "/{cv_id}",
    response_model=AskResponse,
    summary="Ask question about CV",
    description="""
    Ask a question about a specific CV using RAG.
    
    The system retrieves relevant CV chunks based on your question,
    uses them as context, and generates an informed response.
    
    **Features:**
    - Semantic search finds relevant CV sections
    - Conversation history provides context
    - Evaluation summary is included for context
    
    **Example questions:**
    - "What is their Python experience?"
    - "Why did they score low on fintech?"
    - "What are their main strengths?"
    """,
)
@limiter.limit(RATE_LIMIT_CHAT)
async def ask_question(
    request: Request,
    cv_id: uuid.UUID,
    data: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> AskResponse:
    """Ask a question about a CV."""
    return await ChatController.ask_question(
        cv_id=cv_id,
        request=data,
        current_user=current_user,
        chat_service=chat_service,
    )


@router.get(
    "/{cv_id}",
    response_model=ChatHistoryResponse,
    summary="Get chat history",
    description="""
    Get the conversation history for a CV.
    
    Returns all messages in chronological order (oldest first).
    Use the `limit` parameter to get only recent messages.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_history(
    request: Request,
    cv_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Max messages to return (most recent)"
    ),
) -> ChatHistoryResponse:
    """Get chat history for a CV."""
    return await ChatController.get_history(
        cv_id=cv_id,
        current_user=current_user,
        chat_service=chat_service,
        limit=limit,
    )


@router.delete(
    "/{cv_id}",
    summary="Clear chat history",
    description="Delete all messages in the conversation for a CV.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def clear_history(
    request: Request,
    cv_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> dict:
    """Clear chat history for a CV."""
    return await ChatController.clear_history(
        cv_id=cv_id,
        current_user=current_user,
        chat_service=chat_service,
    )


@router.post(
    "/{cv_id}/explain/{criterion}",
    response_model=ExplainCriterionResponse,
    summary="Explain criterion score",
    description="""
    Get a detailed explanation for why a criterion received a specific score.
    
    **Use case:** When a user clicks "Why?" on an evaluation criterion,
    this endpoint generates a detailed breakdown including:
    - Why the score was given
    - Evidence from the CV
    - What would be needed for a higher score
    
    **Criterion names** (case-insensitive):
    - Education
    - Fintech Experience
    - Technical Skills
    - Soft Skills
    - AI-Native Development
    """,
)
@limiter.limit(RATE_LIMIT_CHAT)
async def explain_criterion(
    request: Request,
    cv_id: uuid.UUID,
    criterion: str,
    data: ExplainCriterionRequest = ExplainCriterionRequest(),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ExplainCriterionResponse:
    """Explain a criterion score."""
    return await ChatController.explain_criterion(
        cv_id=cv_id,
        criterion=criterion,
        request=data,
        current_user=current_user,
        chat_service=chat_service,
    )
