"""Base classes for the multi-agent system.

This module defines the abstract base class for all agents and
the shared context object used for dependency injection.

Classes:
    AgentContext: Shared context with database session and repositories.
    BaseAgent: Abstract base class for all agents.

Example:
    Creating a custom agent::
    
        class MyAgent(BaseAgent):
            name = "my_agent"
            supported_tasks = {TaskType.MY_TASK}
            
            async def process(self, message: AgentMessage) -> AgentResult:
                # Implementation here
                return AgentResult.ok({"result": "done"}, self.name)
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.cv.cv_repository import CVRepository
from app.features.cv.evaluation_repository import EvaluationRepository
from app.features.cv.template_repository import TemplateRepository
from app.features.cv.embedding_repository import EmbeddingRepository
from app.features.chat.chat_repository import ChatRepository

from .messages import AgentMessage, AgentResult, AgentStatus, TaskType

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Shared context for agents.
    
    Provides dependency injection of database session and repositories
    to all agents. Created once per request/operation and passed to agents.
    
    Attributes:
        session: AsyncSession for database operations.
        cv_repo: Repository for CV operations.
        evaluation_repo: Repository for evaluation operations.
        template_repo: Repository for template operations.
        embedding_repo: Repository for embedding operations.
        chat_repo: Repository for chat history operations.
    
    Example:
        >>> ctx = AgentContext.create(session)
        >>> cv = await ctx.cv_repo.get_by_id(cv_id)
    """
    session: AsyncSession
    cv_repo: CVRepository
    evaluation_repo: EvaluationRepository
    template_repo: TemplateRepository
    embedding_repo: EmbeddingRepository
    chat_repo: ChatRepository
    
    @classmethod
    def create(cls, session: AsyncSession) -> "AgentContext":
        """Create a new context with all repositories.
        
        Factory method that initializes all repositories with
        the provided database session.
        
        Args:
            session: AsyncSession for database operations.
        
        Returns:
            New AgentContext instance.
        """
        return cls(
            session=session,
            cv_repo=CVRepository(session),
            evaluation_repo=EvaluationRepository(session),
            template_repo=TemplateRepository(session),
            embedding_repo=EmbeddingRepository(session),
            chat_repo=ChatRepository(session),
        )


class BaseAgent(ABC):
    """Abstract base class for all agents.
    
    Defines the interface that all agents must implement and provides
    common functionality for task execution, timing, and error handling.
    
    Attributes:
        name: Unique identifier for the agent.
        supported_tasks: Set of TaskTypes this agent can handle.
        context: Shared AgentContext with repositories.
    
    Subclasses must:
        1. Define class-level `name` and `supported_tasks` attributes.
        2. Implement the `process()` method.
    
    Example:
        Creating a custom agent::
        
            class ParserAgent(BaseAgent):
                name = "parser_agent"
                supported_tasks = {TaskType.PARSE_DOCUMENT, TaskType.EXTRACT_TEXT}
                
                async def process(self, message: AgentMessage) -> AgentResult:
                    # Parse document logic
                    return AgentResult.ok({"text": "..."}, self.name)
    """
    
    # Class-level attributes (must be overridden by subclasses)
    name: str = "base_agent"
    supported_tasks: Set[TaskType] = set()
    
    def __init__(self, context: AgentContext) -> None:
        """Initialize agent with shared context.
        
        Args:
            context: Shared AgentContext with repositories.
        """
        self.context = context
        self._logger = logging.getLogger(f"{__name__}.{self.name}")
    
    @property
    def session(self) -> AsyncSession:
        """Get the database session from context."""
        return self.context.session
    
    def can_handle(self, task_type: TaskType) -> bool:
        """Check if this agent can handle a task type.
        
        Args:
            task_type: The TaskType to check.
        
        Returns:
            True if this agent supports the task type.
        """
        return task_type in self.supported_tasks
    
    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentResult:
        """Process a task message.
        
        This is the main entry point for task execution. Subclasses
        must implement this method with their specific logic.
        
        Args:
            message: The AgentMessage containing task type and payload.
        
        Returns:
            AgentResult with status, data, and optional next task.
        """
        pass
    
    async def execute(self, message: AgentMessage) -> AgentResult:
        """Execute a task with timing and error handling.
        
        Wraps the `process()` method with:
        - Validation that the task type is supported
        - Execution timing
        - Error handling and logging
        
        Args:
            message: The AgentMessage to process.
        
        Returns:
            AgentResult with execution metadata.
        """
        start_time = time.perf_counter()
        
        # Validate task type
        if not self.can_handle(message.task_type):
            return AgentResult.fail(
                error=f"Agent '{self.name}' cannot handle task: {message.task_type}",
                agent_name=self.name,
            )
        
        try:
            self._logger.info(
                f"Processing task: {message.task_type}",
                extra={"correlation_id": message.correlation_id}
            )
            
            # Execute the task
            result = await self.process(message)
            
            # Add timing
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            result.execution_time_ms = elapsed_ms
            result.agent_name = self.name
            
            self._logger.info(
                f"Task completed: {message.task_type} in {elapsed_ms:.2f}ms",
                extra={"correlation_id": message.correlation_id, "status": result.status}
            )
            
            return result
            
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._logger.error(
                f"Task failed: {message.task_type} - {e}",
                exc_info=True,
                extra={"correlation_id": message.correlation_id}
            )
            return AgentResult.fail(
                error=str(e),
                agent_name=self.name,
                execution_time_ms=elapsed_ms,
            )
    
    def __repr__(self) -> str:
        """Return a string representation of the agent."""
        tasks = ", ".join(t.value for t in self.supported_tasks)
        return f"<{self.__class__.__name__}(name={self.name}, tasks=[{tasks}])>"
