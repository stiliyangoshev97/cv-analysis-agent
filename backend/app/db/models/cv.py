"""CV and Evaluation models for document storage and scoring.

This module defines models for storing uploaded CVs, their evaluations,
and vector embeddings for semantic search.

Classes:
    CVStatus: Enum of CV processing states.
    EvaluationStatus: Enum of pass/fail status.
    CV: Uploaded CV document model.
    CVEvaluation: Evaluation results model.
    CVEmbedding: Vector embedding model for semantic search.

Example:
    Creating a CV and evaluation::
    
        cv = CV(
            user_id=user.id,
            filename="john_doe_resume.pdf",
            original_text="John Doe\\nSoftware Engineer..."
        )
        session.add(cv)
        
        evaluation = CVEvaluation(
            cv_id=cv.id,
            template_id=template.id,
            score=75,
            status="pass"
        )
        session.add(evaluation)
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import String, Integer, Text, ForeignKey, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.template import EvaluationTemplate
    from app.db.models.chat import ChatHistory


class CVStatus(str, Enum):
    """CV processing status values.
    
    Values:
        PENDING: CV uploaded, awaiting processing.
        PROCESSING: CV being parsed and evaluated.
        EVALUATED: Evaluation complete.
        ERROR: Processing failed.
    """
    PENDING = "pending"
    PROCESSING = "processing"
    EVALUATED = "evaluated"
    ERROR = "error"


class EvaluationStatus(str, Enum):
    """Evaluation result status values.
    
    Values:
        PASS: CV met passing criteria.
        FAIL: CV did not meet passing criteria.
    """
    PASS = "pass"
    FAIL = "fail"


class CV(Base):
    """Uploaded CV document model.
    
    Stores metadata and extracted text from uploaded PDF resumes.
    
    Attributes:
        id: Unique CV identifier (UUID).
        user_id: Foreign key to users table.
        filename: Original uploaded filename.
        original_text: Extracted text content.
        candidate_name: Extracted candidate name (if available).
        status: Processing status (pending/processing/evaluated/error).
        uploaded_at: Upload timestamp.
        
    Relationships:
        user: The user who uploaded this CV.
        evaluations: List of evaluations for this CV.
        embeddings: Vector embeddings for semantic search.
        chat_history: Chat messages about this CV.
    
    Example:
        >>> cv = CV(
        ...     user_id=user.id,
        ...     filename="resume.pdf",
        ...     original_text="Jane Smith\\nSenior Developer..."
        ... )
    """
    
    __tablename__ = "cvs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Document metadata
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    original_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    candidate_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    # Processing status
    status: Mapped[str] = mapped_column(
        String(20),
        default=CVStatus.PENDING.value,
        nullable=False,
    )
    
    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="cvs",
    )
    
    evaluations: Mapped[List["CVEvaluation"]] = relationship(
        "CVEvaluation",
        back_populates="cv",
        cascade="all, delete-orphan",
    )
    
    embeddings: Mapped[List["CVEmbedding"]] = relationship(
        "CVEmbedding",
        back_populates="cv",
        cascade="all, delete-orphan",
    )
    
    chat_history: Mapped[List["ChatHistory"]] = relationship(
        "ChatHistory",
        back_populates="cv",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<CV '{self.filename}' ({self.status})>"


class CVEvaluation(Base):
    """Evaluation results for a CV.
    
    Stores the scoring results from evaluating a CV against a template.
    
    Attributes:
        id: Unique evaluation identifier (UUID).
        cv_id: Foreign key to cvs table.
        template_id: Foreign key to evaluation_templates table.
        score: Total score achieved (0-100).
        status: Pass or fail result.
        reasoning: AI-generated explanation of the evaluation.
        criteria_results: JSON object with per-criterion scores.
        evaluated_at: Evaluation timestamp.
        
    Relationships:
        cv: The CV that was evaluated.
        template: The template used for evaluation.
    
    Example:
        >>> evaluation = CVEvaluation(
        ...     cv_id=cv.id,
        ...     template_id=template.id,
        ...     score=78,
        ...     status="pass",
        ...     criteria_results={"technical_skills": {"score": 22, "met": True}}
        ... )
    """
    
    __tablename__ = "cv_evaluations"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign keys
    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evaluation_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Evaluation results
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    reasoning: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Per-criterion results (JSON)
    criteria_results: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    
    # Timestamp
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    cv: Mapped["CV"] = relationship(
        "CV",
        back_populates="evaluations",
    )
    template: Mapped[Optional["EvaluationTemplate"]] = relationship(
        "EvaluationTemplate",
        back_populates="evaluations",
    )
    
    def __repr__(self) -> str:
        return f"<CVEvaluation {self.score} ({self.status})>"


class CVEmbedding(Base):
    """Vector embedding for a CV chunk.
    
    Stores the vector embedding generated from CV text for semantic search.
    Uses pgvector extension for efficient similarity queries.
    Each CV may have multiple embeddings (one per chunk).
    
    Attributes:
        id: Unique embedding identifier (UUID).
        cv_id: Foreign key to cvs table.
        chunk_text: The text content this embedding represents.
        chunk_index: Position of this chunk in the document (0-based).
        embedding: Vector embedding (1536 dimensions for OpenAI).
        created_at: Embedding generation timestamp.
        
    Relationships:
        cv: The CV this embedding represents.
    
    Example:
        >>> from pgvector.sqlalchemy import Vector
        >>> embedding = CVEmbedding(
        ...     cv_id=cv.id,
        ...     chunk_text="John Doe, Software Engineer...",
        ...     chunk_index=0,
        ...     embedding=[0.1, 0.2, 0.3, ...]  # 1536 floats
        ... )
    
    Note:
        Requires pgvector extension to be installed in PostgreSQL.
        Run: CREATE EXTENSION vector;
    """
    
    __tablename__ = "cv_embeddings"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign key to CV
    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Chunk text content
    chunk_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Chunk position in document
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    # Note: Vector column will be added via Alembic migration
    # because SQLAlchemy mapped_column doesn't directly support pgvector
    # We'll use raw SQL in the migration for the vector column
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    cv: Mapped["CV"] = relationship(
        "CV",
        back_populates="embeddings",
    )
    
    def __repr__(self) -> str:
        return f"<CVEmbedding for CV {self.cv_id} chunk {self.chunk_index}>"
