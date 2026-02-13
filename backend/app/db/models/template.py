"""Evaluation Template models for CV scoring criteria.

This module defines models for evaluation templates and their criteria.
Templates can be system-provided (read-only) or user-created (editable).

Classes:
    EvaluationTemplate: Template containing evaluation configuration.
    TemplateCriterion: Individual criterion within a template.

Example:
    Creating a custom template::
    
        template = EvaluationTemplate(
            user_id=user.id,
            name="Junior Developer Screening",
            description="Criteria for entry-level positions",
            passing_score=50,
            minimum_criteria_met=2
        )
        session.add(template)
        
        criterion = TemplateCriterion(
            template_id=template.id,
            name="Technical Skills",
            max_points=30,
            is_required=True
        )
        session.add(criterion)
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.cv import CVEvaluation


class EvaluationTemplate(Base, TimestampMixin):
    """Evaluation template for CV scoring.
    
    Contains configuration for how CVs should be evaluated, including
    passing thresholds and relationships to criteria.
    
    Attributes:
        id: Unique template identifier (UUID).
        user_id: Foreign key to users table (null for system templates).
        name: Template display name.
        description: Optional template description.
        is_system_template: Whether this is a read-only system template.
        passing_score: Minimum score to pass (0-100).
        minimum_criteria_met: Minimum number of criteria that must be met.
        
    Relationships:
        user: The user who owns this template (null for system).
        criteria: List of criteria in this template.
        evaluations: Evaluations using this template.
    
    Example:
        >>> template = EvaluationTemplate(
        ...     name="AI-First Fintech",
        ...     is_system_template=True,
        ...     passing_score=60,
        ...     minimum_criteria_met=3
        ... )
    """
    
    __tablename__ = "evaluation_templates"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign key to user (null for system templates)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # Template metadata
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # System template flag (read-only)
    is_system_template: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    
    # Scoring configuration
    passing_score: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )
    minimum_criteria_met: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="templates",
        foreign_keys=[user_id],
    )
    
    criteria: Mapped[List["TemplateCriterion"]] = relationship(
        "TemplateCriterion",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateCriterion.sort_order",
    )
    
    evaluations: Mapped[List["CVEvaluation"]] = relationship(
        "CVEvaluation",
        back_populates="template",
    )
    
    def __repr__(self) -> str:
        template_type = "system" if self.is_system_template else "user"
        return f"<EvaluationTemplate '{self.name}' ({template_type})>"


class TemplateCriterion(Base):
    """Individual criterion within an evaluation template.
    
    Defines a single scoring criterion with points, keywords,
    and evaluation guidelines for the AI.
    
    Attributes:
        id: Unique criterion identifier (UUID).
        template_id: Foreign key to evaluation_templates table.
        name: Criterion display name (e.g., "Technical Skills").
        description: Human-readable description.
        max_points: Maximum points for this criterion.
        keywords: JSON array of keywords for AI hints.
        evaluation_guidelines: Detailed instructions for AI evaluation.
        is_required: Whether this criterion must be met for passing.
        sort_order: Display order within template.
        
    Relationships:
        template: The template this criterion belongs to.
    
    Example:
        >>> criterion = TemplateCriterion(
        ...     template_id=template.id,
        ...     name="Technical Skills",
        ...     description="Programming languages and frameworks",
        ...     max_points=25,
        ...     keywords=["Python", "TypeScript", "React"],
        ...     is_required=True,
        ...     sort_order=1
        ... )
    """
    
    __tablename__ = "template_criteria"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign key to template
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evaluation_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Criterion details
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    max_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    # AI hints
    keywords: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    evaluation_guidelines: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Scoring flags
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    
    # Display order
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    
    # Timestamps (just created_at for criteria)
    created_at: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    
    # Relationships
    template: Mapped["EvaluationTemplate"] = relationship(
        "EvaluationTemplate",
        back_populates="criteria",
    )
    
    def __repr__(self) -> str:
        return f"<TemplateCriterion '{self.name}' ({self.max_points} pts)>"
