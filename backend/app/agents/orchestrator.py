"""Agent Orchestrator for task routing and workflow management.

This module provides the central orchestrator that coordinates
all agents, routes tasks, and manages multi-step workflows.

The orchestrator acts as a supervisor/router pattern:
- Receives task requests
- Routes to appropriate agent
- Handles task chaining (next_task)
- Manages errors and retries

Classes:
    AgentOrchestrator: Central coordinator for all agents.

Example:
    Using the orchestrator::
    
        async with get_db_session() as session:
            orchestrator = AgentOrchestrator(session)
            result = await orchestrator.execute(
                task_type=TaskType.UPLOAD_CV,
                payload={"file_content": bytes, "filename": "resume.pdf"},
                user_id=current_user.id
            )
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseAgent, AgentContext
from .messages import AgentMessage, AgentResult, AgentStatus, TaskType
from .parser_agent import ParserAgent
from .scorer_agent import ScorerAgent
from .chat_agent import ChatAgent
from .notification_agent import NotificationAgent

logger = logging.getLogger(__name__)


@dataclass
class WorkflowResult:
    """Result from a multi-step workflow.
    
    Aggregates results from all agents involved in a workflow.
    
    Attributes:
        success: Whether the overall workflow succeeded.
        final_result: The result from the last agent.
        steps: List of all agent results in order.
        total_time_ms: Total execution time across all agents.
        error: Error message if workflow failed.
    """
    success: bool
    final_result: Optional[AgentResult] = None
    steps: List[AgentResult] = field(default_factory=list)
    total_time_ms: float = 0.0
    error: Optional[str] = None
    
    @property
    def data(self) -> Optional[dict]:
        """Get data from final result."""
        return self.final_result.data if self.final_result else None


class AgentOrchestrator:
    """Central orchestrator for agent coordination.
    
    Routes tasks to appropriate agents and manages multi-step
    workflows. Acts as the entry point for all agent operations.
    
    Architecture:
        The orchestrator maintains a registry of agents and their
        supported task types. When a task is received:
        
        1. Find the agent that handles the task type
        2. Create an AgentMessage with the payload
        3. Execute the agent
        4. If result has next_task, continue the chain
        5. Return the final result
    
    Attributes:
        context: Shared AgentContext with repositories.
        agents: Dictionary mapping agent names to instances.
        task_routing: Dictionary mapping TaskType to agent name.
    
    Supported Workflows:
        UPLOAD_CV: ParserAgent → ScorerAgent → NotificationAgent
        RE_EVALUATE: ScorerAgent → NotificationAgent
        ASK_QUESTION: ChatAgent
        And more...
    
    Example:
        >>> orchestrator = AgentOrchestrator(session)
        >>> result = await orchestrator.execute(
        ...     task_type=TaskType.UPLOAD_CV,
        ...     payload={"file_content": pdf_bytes, "filename": "cv.pdf"},
        ...     user_id=user_id
        ... )
        >>> if result.success:
        ...     print(f"CV uploaded: {result.data['cv_id']}")
    """
    
    # Agent classes to instantiate
    AGENT_CLASSES: List[Type[BaseAgent]] = [
        ParserAgent,
        ScorerAgent,
        ChatAgent,
        NotificationAgent,
    ]
    
    # Maximum chain depth to prevent infinite loops
    MAX_CHAIN_DEPTH = 10
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize orchestrator with database session.
        
        Creates the shared context and instantiates all agents.
        
        Args:
            session: AsyncSession for database operations.
        """
        self.context = AgentContext.create(session)
        self.agents: Dict[str, BaseAgent] = {}
        self.task_routing: Dict[TaskType, str] = {}
        
        # Instantiate all agents
        for agent_class in self.AGENT_CLASSES:
            agent = agent_class(self.context)
            self.agents[agent.name] = agent
            
            # Build routing table
            for task_type in agent.supported_tasks:
                self.task_routing[task_type] = agent.name
        
        logger.info(
            f"Orchestrator initialized with {len(self.agents)} agents, "
            f"supporting {len(self.task_routing)} task types"
        )
    
    def get_agent(self, task_type: TaskType) -> Optional[BaseAgent]:
        """Get the agent that handles a task type.
        
        Args:
            task_type: The TaskType to look up.
        
        Returns:
            The agent instance, or None if not found.
        """
        agent_name = self.task_routing.get(task_type)
        if agent_name:
            return self.agents.get(agent_name)
        return None
    
    async def execute(
        self,
        task_type: TaskType,
        payload: dict,
        user_id: Optional[uuid.UUID] = None,
        cv_id: Optional[uuid.UUID] = None,
        follow_chain: bool = True,
    ) -> WorkflowResult:
        """Execute a task, optionally following the chain.
        
        Main entry point for agent operations. Creates a message,
        routes to the appropriate agent, and optionally follows
        the task chain (next_task).
        
        Args:
            task_type: The type of task to execute.
            payload: Task-specific data.
            user_id: Optional user UUID for authorization.
            cv_id: Optional CV UUID for context.
            follow_chain: Whether to follow next_task chain.
        
        Returns:
            WorkflowResult with all step results.
        
        Example:
            >>> result = await orchestrator.execute(
            ...     TaskType.ASK_QUESTION,
            ...     payload={"question": "What's their experience?"},
            ...     user_id=user_id,
            ...     cv_id=cv_id
            ... )
        """
        start_time = time.perf_counter()
        steps: List[AgentResult] = []
        
        # Build initial metadata
        metadata = {
            "correlation_id": str(uuid.uuid4()),
        }
        if user_id:
            metadata["user_id"] = user_id
        if cv_id:
            metadata["cv_id"] = cv_id
        
        current_task = task_type
        current_payload = payload
        chain_depth = 0
        
        logger.info(
            f"Starting workflow: {task_type}",
            extra={"correlation_id": metadata["correlation_id"]}
        )
        
        while current_task and chain_depth < self.MAX_CHAIN_DEPTH:
            chain_depth += 1
            
            # Find agent
            agent = self.get_agent(current_task)
            if not agent:
                error = f"No agent found for task: {current_task}"
                logger.error(error)
                return WorkflowResult(
                    success=False,
                    steps=steps,
                    total_time_ms=(time.perf_counter() - start_time) * 1000,
                    error=error,
                )
            
            # Create message
            message = AgentMessage(
                task_type=current_task,
                payload=current_payload,
                metadata=metadata,
            )
            
            # Execute agent
            logger.debug(f"Executing {agent.name} for {current_task}")
            result = await agent.execute(message)
            steps.append(result)
            
            # Check for failure
            if result.failed:
                logger.error(f"Task failed: {current_task} - {result.error}")
                return WorkflowResult(
                    success=False,
                    final_result=result,
                    steps=steps,
                    total_time_ms=(time.perf_counter() - start_time) * 1000,
                    error=result.error,
                )
            
            # Check for chain continuation
            if follow_chain and result.next_task:
                logger.debug(f"Chaining to: {result.next_task}")
                current_task = result.next_task
                # Merge result data into payload for next task
                current_payload = {**current_payload, **(result.data or {})}
            else:
                current_task = None
        
        if chain_depth >= self.MAX_CHAIN_DEPTH:
            logger.warning(f"Chain depth limit reached: {self.MAX_CHAIN_DEPTH}")
        
        total_time = (time.perf_counter() - start_time) * 1000
        
        logger.info(
            f"Workflow completed: {len(steps)} steps in {total_time:.2f}ms",
            extra={"correlation_id": metadata["correlation_id"]}
        )
        
        return WorkflowResult(
            success=True,
            final_result=steps[-1] if steps else None,
            steps=steps,
            total_time_ms=total_time,
        )
    
    async def execute_single(
        self,
        task_type: TaskType,
        payload: dict,
        user_id: Optional[uuid.UUID] = None,
        cv_id: Optional[uuid.UUID] = None,
    ) -> AgentResult:
        """Execute a single task without following the chain.
        
        Convenience method for one-off tasks that don't need
        workflow chaining.
        
        Args:
            task_type: The type of task to execute.
            payload: Task-specific data.
            user_id: Optional user UUID.
            cv_id: Optional CV UUID.
        
        Returns:
            AgentResult from the single task.
        """
        result = await self.execute(
            task_type=task_type,
            payload=payload,
            user_id=user_id,
            cv_id=cv_id,
            follow_chain=False,
        )
        return result.final_result or AgentResult.fail(
            "No result from task",
            agent_name="orchestrator",
        )
    
    async def upload_cv(
        self,
        file_content: bytes,
        filename: str,
        user_id: uuid.UUID,
        template_id: Optional[uuid.UUID] = None,
    ) -> WorkflowResult:
        """Convenience method for CV upload workflow.
        
        Executes the full pipeline: parse → evaluate → notify.
        
        Args:
            file_content: Raw file bytes.
            filename: Original filename.
            user_id: User UUID.
            template_id: Optional evaluation template UUID.
        
        Returns:
            WorkflowResult with CV ID and evaluation results.
        
        Example:
            >>> result = await orchestrator.upload_cv(
            ...     file_content=pdf_bytes,
            ...     filename="resume.pdf",
            ...     user_id=current_user.id
            ... )
            >>> print(result.data["cv_id"])
        """
        payload = {
            "file_content": file_content,
            "filename": filename,
        }
        if template_id:
            payload["template_id"] = str(template_id)
        
        # Start with parse, which chains to evaluate
        return await self.execute(
            task_type=TaskType.PARSE_DOCUMENT,
            payload=payload,
            user_id=user_id,
        )
    
    async def ask_question(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        question: str,
    ) -> AgentResult:
        """Convenience method for asking questions about a CV.
        
        Args:
            cv_id: UUID of the CV.
            user_id: UUID of the user.
            question: Question to ask.
        
        Returns:
            AgentResult with response.
        """
        return await self.execute_single(
            task_type=TaskType.ASK_QUESTION,
            payload={"question": question},
            user_id=user_id,
            cv_id=cv_id,
        )
    
    async def re_evaluate(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        template_id: Optional[uuid.UUID] = None,
    ) -> WorkflowResult:
        """Convenience method for re-evaluating a CV.
        
        Args:
            cv_id: UUID of the CV.
            user_id: UUID of the user.
            template_id: Optional new template UUID.
        
        Returns:
            WorkflowResult with new evaluation results.
        """
        payload = {}
        if template_id:
            payload["template_id"] = str(template_id)
        
        return await self.execute(
            task_type=TaskType.RE_EVALUATE,
            payload=payload,
            user_id=user_id,
            cv_id=cv_id,
        )
    
    def get_supported_tasks(self) -> List[str]:
        """Get list of all supported task types.
        
        Returns:
            List of task type values.
        """
        return [t.value for t in self.task_routing.keys()]
    
    def get_agent_info(self) -> Dict[str, dict]:
        """Get information about all registered agents.
        
        Returns:
            Dictionary with agent info.
        """
        return {
            name: {
                "tasks": [t.value for t in agent.supported_tasks],
                "class": agent.__class__.__name__,
            }
            for name, agent in self.agents.items()
        }
