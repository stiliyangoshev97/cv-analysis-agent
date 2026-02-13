"""Multi-Agent System for CV Screening.

This module provides a coordinated multi-agent architecture where
specialized agents handle specific tasks and communicate through
a central orchestrator.

Architecture:
    AgentOrchestrator (Supervisor/Router)
           │
    ┌──────┼──────┬──────────┬────────────┐
    ▼      ▼      ▼          ▼            ▼
  Parser  Scorer  Chat   Notification   ...
  Agent   Agent   Agent     Agent

Agents:
    ParserAgent: Document parsing (PDF/DOCX extraction, chunking)
    ScorerAgent: CV evaluation and embedding generation
    ChatAgent: RAG-powered Q&A conversations
    NotificationAgent: Email/WhatsApp alerts (stub for Phase 5)

Usage:
    from app.agents import AgentOrchestrator, TaskType
    
    orchestrator = AgentOrchestrator(session)
    result = await orchestrator.execute(
        task_type=TaskType.UPLOAD_CV,
        payload={"file_content": bytes, "filename": "resume.pdf"},
        user_id=user.id
    )
"""

from .messages import TaskType, AgentMessage, AgentResult, AgentStatus
from .base import BaseAgent, AgentContext
from .parser_agent import ParserAgent
from .scorer_agent import ScorerAgent
from .chat_agent import ChatAgent
from .notification_agent import NotificationAgent
from .orchestrator import AgentOrchestrator, WorkflowResult
from .tools import (
    validate_file,
    extract_candidate_name,
    format_criteria_results,
    DocumentTools,
    EmbeddingTools,
    EvaluationTools,
    ConversationTools,
)

__all__ = [
    # Message Types
    "TaskType",
    "AgentMessage",
    "AgentResult",
    "AgentStatus",
    # Base
    "BaseAgent",
    "AgentContext",
    # Agents
    "ParserAgent",
    "ScorerAgent",
    "ChatAgent",
    "NotificationAgent",
    # Orchestrator
    "AgentOrchestrator",
    "WorkflowResult",
    # Tools
    "validate_file",
    "extract_candidate_name",
    "format_criteria_results",
    "DocumentTools",
    "EmbeddingTools",
    "EvaluationTools",
    "ConversationTools",
]
