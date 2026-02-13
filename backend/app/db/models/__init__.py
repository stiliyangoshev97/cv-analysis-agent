"""SQLAlchemy ORM models for CV Screening Agent.

This module exports all database models used in the application.

Models:
    User: User accounts and authentication.
    UserApiKey: Encrypted API keys for AI providers.
    UserAgentConfig: Per-agent AI provider configuration.
    EvaluationTemplate: CV evaluation templates (system + user).
    TemplateCriterion: Individual criteria within templates.
    CV: Uploaded CV documents.
    CVEvaluation: Evaluation results for CVs.
    CVEmbedding: Vector embeddings for semantic search.
    ChatHistory: Conversation history for CV explanations.
    NotificationSettings: User notification preferences.

Example:
    Importing models::
    
        from app.db.models import User, CV, CVEvaluation
        
        # Query users
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
"""

from app.db.models.user import User
from app.db.models.api_key import UserApiKey
from app.db.models.agent_config import UserAgentConfig
from app.db.models.template import EvaluationTemplate, TemplateCriterion
from app.db.models.cv import CV, CVEvaluation, CVEmbedding
from app.db.models.chat import ChatHistory
from app.db.models.notification import NotificationSettings

__all__ = [
    # User & Auth
    "User",
    "UserApiKey",
    "UserAgentConfig",
    
    # Templates
    "EvaluationTemplate",
    "TemplateCriterion",
    
    # CV & Evaluation
    "CV",
    "CVEvaluation",
    "CVEmbedding",
    
    # Chat & Notifications
    "ChatHistory",
    "NotificationSettings",
]
