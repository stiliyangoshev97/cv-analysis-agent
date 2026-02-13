"""Chat feature Pydantic schemas.

This module defines request and response models for the chat endpoints.
All schemas use Pydantic for validation and serialization.

Schemas:
    ChatMessageRequest: Request body for sending a chat message.
    ChatMessageResponse: Single chat message response.
    ChatHistoryResponse: Full conversation history response.
    ExplainCriterionRequest: Request for criterion explanation.
    ExplainCriterionResponse: Response with score explanation.
    CompareRequest: Request to compare multiple CVs.
    CompareResponse: Response with comparison analysis.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request body for sending a chat message.
    
    Attributes:
        message: The user's question about the CV.
    
    Example:
        >>> request = ChatMessageRequest(
        ...     message="What is their Python experience?"
        ... )
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question about the CV"
    )


class ChatMessageResponse(BaseModel):
    """Single chat message in a conversation.
    
    Attributes:
        id: Unique message identifier.
        role: Message sender (user or assistant).
        content: Message text content.
        created_at: When the message was created.
        sources: Optional list of CV chunk references used.
    """
    id: uuid.UUID = Field(description="Message UUID")
    role: str = Field(description="Message sender: 'user' or 'assistant'")
    content: str = Field(description="Message text content")
    created_at: datetime = Field(description="Message creation timestamp")
    sources: List[str] = Field(
        default_factory=list,
        description="CV chunk excerpts used as context (for assistant messages)"
    )
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Full conversation history for a CV.
    
    Attributes:
        cv_id: The CV this conversation is about.
        messages: List of messages in chronological order.
        total: Total number of messages.
    """
    cv_id: uuid.UUID = Field(description="CV UUID")
    messages: List[ChatMessageResponse] = Field(
        description="Messages in chronological order"
    )
    total: int = Field(description="Total number of messages")


class ExplainCriterionRequest(BaseModel):
    """Request body for criterion explanation.
    
    The criterion name comes from the URL path parameter.
    This schema allows optional additional context.
    
    Attributes:
        include_cv_evidence: Whether to include CV excerpts in response.
    """
    include_cv_evidence: bool = Field(
        default=True,
        description="Include relevant CV excerpts in explanation"
    )


class ExplainCriterionResponse(BaseModel):
    """Response with detailed criterion score explanation.
    
    Attributes:
        criterion: Name of the criterion explained.
        score: Actual score received.
        max_score: Maximum possible score.
        explanation: AI-generated detailed explanation.
        evidence: Relevant CV excerpts supporting the score.
    """
    criterion: str = Field(description="Criterion name")
    score: int = Field(description="Score received")
    max_score: int = Field(description="Maximum possible score")
    explanation: str = Field(description="Detailed AI explanation")
    evidence: List[str] = Field(
        default_factory=list,
        description="Relevant CV excerpts"
    )


class CompareRequest(BaseModel):
    """Request to compare multiple CVs.
    
    Attributes:
        cv_ids: List of CV UUIDs to compare (2-5 CVs).
        question: Comparison question or focus area.
    
    Example:
        >>> request = CompareRequest(
        ...     cv_ids=[uuid1, uuid2],
        ...     question="Compare their fintech experience"
        ... )
    """
    cv_ids: List[uuid.UUID] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="CV UUIDs to compare (2-5 CVs)"
    )
    question: str = Field(
        default="Compare these candidates overall",
        max_length=1000,
        description="Comparison question or focus area"
    )


class CompareResponse(BaseModel):
    """Response with CV comparison analysis.
    
    Attributes:
        cv_ids: CVs that were compared.
        comparison: AI-generated comparison analysis.
        ranking: Optional ranking with brief justification.
    """
    cv_ids: List[uuid.UUID] = Field(description="CVs compared")
    comparison: str = Field(description="Detailed comparison analysis")
    ranking: Optional[List[dict]] = Field(
        default=None,
        description="Ranking with cv_id and reason"
    )


class AskResponse(BaseModel):
    """Response from asking a question about a CV.
    
    Combines the assistant's response with metadata.
    
    Attributes:
        message: The assistant's response message.
        sources_used: Number of CV chunks used as context.
    """
    message: ChatMessageResponse = Field(description="Assistant response")
    sources_used: int = Field(
        default=0,
        description="Number of CV chunks used as context"
    )
