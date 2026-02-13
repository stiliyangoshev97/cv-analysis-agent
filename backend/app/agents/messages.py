"""Message types for agent communication.

This module defines the data structures used for communication
between agents and the orchestrator.

Classes:
    TaskType: Enum of all supported task types.
    AgentStatus: Enum of task execution statuses.
    AgentMessage: Input message to an agent.
    AgentResult: Output result from an agent.

Example:
    Creating a message for CV upload::
    
        message = AgentMessage(
            task_type=TaskType.UPLOAD_CV,
            payload={"file_content": bytes, "filename": "resume.pdf"},
            metadata={"user_id": user.id, "correlation_id": uuid4()}
        )
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class TaskType(str, Enum):
    """Supported task types for agents.
    
    Categories:
        Document Tasks: PARSE_DOCUMENT, EXTRACT_TEXT
        Scoring Tasks: EVALUATE_CV, GENERATE_EMBEDDINGS, RE_EVALUATE
        Chat Tasks: ASK_QUESTION, EXPLAIN_SCORE, COMPARE_CVS
        Notification Tasks: SEND_EMAIL, SEND_WHATSAPP, CHECK_THRESHOLD
        Workflow Tasks: UPLOAD_CV (combines parse + score + notify)
    """
    # Document Tasks (ParserAgent)
    PARSE_DOCUMENT = "parse_document"
    EXTRACT_TEXT = "extract_text"
    
    # Scoring Tasks (ScorerAgent)
    EVALUATE_CV = "evaluate_cv"
    GENERATE_EMBEDDINGS = "generate_embeddings"
    RE_EVALUATE = "re_evaluate"
    
    # Chat Tasks (ChatAgent)
    ASK_QUESTION = "ask_question"
    EXPLAIN_SCORE = "explain_score"
    COMPARE_CVS = "compare_cvs"
    GET_CHAT_HISTORY = "get_chat_history"
    CLEAR_CHAT_HISTORY = "clear_chat_history"
    
    # Notification Tasks (NotificationAgent)
    SEND_EMAIL = "send_email"
    SEND_WHATSAPP = "send_whatsapp"
    CHECK_THRESHOLD = "check_threshold"
    DISPATCH_NOTIFICATION = "dispatch_notification"
    
    # Workflow Tasks (Orchestrator)
    UPLOAD_CV = "upload_cv"  # Full pipeline: parse → score → notify


class AgentStatus(str, Enum):
    """Status of agent task execution.
    
    Values:
        PENDING: Task is queued.
        RUNNING: Task is being executed.
        SUCCESS: Task completed successfully.
        FAILED: Task failed with error.
        SKIPPED: Task was skipped (e.g., notification not enabled).
    """
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentMessage:
    """Input message to an agent.
    
    Attributes:
        task_type: The type of task to execute.
        payload: Task-specific data (file content, CV text, question, etc.).
        metadata: Context metadata (user_id, cv_id, correlation_id).
        created_at: When the message was created.
    
    Example:
        >>> message = AgentMessage(
        ...     task_type=TaskType.EVALUATE_CV,
        ...     payload={"cv_text": "...", "template_id": None},
        ...     metadata={"user_id": uuid, "cv_id": uuid}
        ... )
    """
    task_type: TaskType
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def user_id(self) -> Optional[uuid.UUID]:
        """Get user_id from metadata."""
        uid = self.metadata.get("user_id")
        if isinstance(uid, str):
            return uuid.UUID(uid)
        return uid
    
    @property
    def cv_id(self) -> Optional[uuid.UUID]:
        """Get cv_id from metadata."""
        cid = self.metadata.get("cv_id")
        if isinstance(cid, str):
            return uuid.UUID(cid)
        return cid
    
    @property
    def correlation_id(self) -> str:
        """Get or generate correlation_id for tracing."""
        return self.metadata.get("correlation_id", str(uuid.uuid4()))


@dataclass
class AgentResult:
    """Output result from an agent.
    
    Attributes:
        status: Execution status (SUCCESS, FAILED, etc.).
        data: Result data on success.
        error: Error message on failure.
        next_task: Optional next task to execute (for chaining).
        agent_name: Name of the agent that produced this result.
        execution_time_ms: How long the task took in milliseconds.
        created_at: When the result was created.
    
    Example:
        >>> result = AgentResult(
        ...     status=AgentStatus.SUCCESS,
        ...     data={"cv_id": uuid, "score": 85},
        ...     agent_name="ScorerAgent"
        ... )
    """
    status: AgentStatus
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    next_task: Optional[TaskType] = None
    agent_name: str = "unknown"
    execution_time_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success(self) -> bool:
        """Check if the task succeeded."""
        return self.status == AgentStatus.SUCCESS
    
    @property
    def failed(self) -> bool:
        """Check if the task failed."""
        return self.status == AgentStatus.FAILED
    
    @classmethod
    def ok(
        cls,
        data: dict[str, Any],
        agent_name: str = "unknown",
        next_task: Optional[TaskType] = None,
        execution_time_ms: float = 0.0,
    ) -> "AgentResult":
        """Create a success result.
        
        Args:
            data: Result data.
            agent_name: Name of the agent.
            next_task: Optional next task to execute.
            execution_time_ms: Execution time.
        
        Returns:
            AgentResult with SUCCESS status.
        """
        return cls(
            status=AgentStatus.SUCCESS,
            data=data,
            agent_name=agent_name,
            next_task=next_task,
            execution_time_ms=execution_time_ms,
        )
    
    @classmethod
    def fail(
        cls,
        error: str,
        agent_name: str = "unknown",
        execution_time_ms: float = 0.0,
    ) -> "AgentResult":
        """Create a failure result.
        
        Args:
            error: Error message.
            agent_name: Name of the agent.
            execution_time_ms: Execution time.
        
        Returns:
            AgentResult with FAILED status.
        """
        return cls(
            status=AgentStatus.FAILED,
            error=error,
            agent_name=agent_name,
            execution_time_ms=execution_time_ms,
        )
    
    @classmethod
    def skip(
        cls,
        reason: str,
        agent_name: str = "unknown",
    ) -> "AgentResult":
        """Create a skipped result.
        
        Args:
            reason: Why the task was skipped.
            agent_name: Name of the agent.
        
        Returns:
            AgentResult with SKIPPED status.
        """
        return cls(
            status=AgentStatus.SKIPPED,
            data={"reason": reason},
            agent_name=agent_name,
        )
