"""Scorer Agent for CV evaluation and embeddings.

This agent handles evaluation tasks including embedding generation,
CV scoring against criteria templates, and re-evaluation.

Tasks:
    EVALUATE_CV: Evaluate a CV against criteria template.
    GENERATE_EMBEDDINGS: Generate and store vector embeddings.
    RE_EVALUATE: Re-evaluate an existing CV.

Example:
    Using the scorer agent::
    
        agent = ScorerAgent(context)
        result = await agent.execute(AgentMessage(
            task_type=TaskType.EVALUATE_CV,
            payload={"cv_text": "...", "cv_id": uuid},
            metadata={"user_id": uuid}
        ))
"""

import logging
import uuid
from typing import Set, Optional

from app.db.models.cv import CV, CVStatus, CVEvaluation, EvaluationStatus

from .base import BaseAgent, AgentContext
from .messages import AgentMessage, AgentResult, TaskType
from .tools import format_criteria_results, EmbeddingTools, EvaluationTools

logger = logging.getLogger(__name__)


class ScorerAgent(BaseAgent):
    """Agent for CV evaluation and embedding generation.
    
    Handles scoring CVs against criteria templates using LangChain
    and manages vector embeddings for RAG retrieval.
    
    Supported Tasks:
        - EVALUATE_CV: Full evaluation with template
        - GENERATE_EMBEDDINGS: Store embeddings for CV chunks
        - RE_EVALUATE: Re-evaluate existing CV
    
    Example:
        >>> agent = ScorerAgent(context)
        >>> result = await agent.execute(AgentMessage(
        ...     task_type=TaskType.EVALUATE_CV,
        ...     payload={"cv_text": text, "chunks": chunks},
        ...     metadata={"cv_id": cv_id, "user_id": user_id}
        ... ))
    """
    
    name = "scorer_agent"
    supported_tasks: Set[TaskType] = {
        TaskType.EVALUATE_CV,
        TaskType.GENERATE_EMBEDDINGS,
        TaskType.RE_EVALUATE,
    }
    
    def __init__(self, context: AgentContext) -> None:
        """Initialize scorer agent.
        
        Args:
            context: Shared AgentContext with repositories.
        """
        super().__init__(context)
        self.embedding_tools = EmbeddingTools(context.session)
        self.evaluation_tools = EvaluationTools()
    
    async def process(self, message: AgentMessage) -> AgentResult:
        """Process an evaluation task.
        
        Routes to appropriate handler based on task type.
        
        Args:
            message: AgentMessage with CV data.
        
        Returns:
            AgentResult with evaluation results.
        """
        if message.task_type == TaskType.EVALUATE_CV:
            return await self._evaluate_cv(message)
        elif message.task_type == TaskType.GENERATE_EMBEDDINGS:
            return await self._generate_embeddings(message)
        elif message.task_type == TaskType.RE_EVALUATE:
            return await self._re_evaluate(message)
        else:
            return AgentResult.fail(
                f"Unknown task type: {message.task_type}",
                agent_name=self.name,
            )
    
    async def _evaluate_cv(self, message: AgentMessage) -> AgentResult:
        """Evaluate a CV against criteria template.
        
        1. Gets or creates CV record
        2. Generates embeddings if chunks provided
        3. Gets evaluation template
        4. Evaluates CV using LangChain
        5. Stores evaluation results
        
        Args:
            message: AgentMessage with cv_text, chunks, cv_id.
        
        Returns:
            AgentResult with evaluation score and details.
        """
        # Extract payload
        cv_text = message.payload.get("cv_text") or message.payload.get("full_text")
        chunks = message.payload.get("chunks", [])
        cv_id = message.cv_id or message.payload.get("cv_id")
        user_id = message.user_id
        template_id = message.payload.get("template_id")
        filename = message.payload.get("filename", "unknown.pdf")
        candidate_name = message.payload.get("candidate_name")
        
        if not cv_text:
            return AgentResult.fail("Missing cv_text in payload", self.name)
        
        self._logger.info(f"Evaluating CV: {cv_id or 'new'}")
        
        # Create CV record if needed
        if not cv_id:
            if not user_id:
                return AgentResult.fail("user_id required for new CV", self.name)
            
            cv = CV(
                user_id=user_id,
                filename=filename,
                original_text=cv_text,
                candidate_name=candidate_name,
                status=CVStatus.PROCESSING.value,
            )
            cv = await self.context.cv_repo.create(cv)
            cv_id = cv.id
            self._logger.debug(f"Created CV record: {cv_id}")
        else:
            cv = await self.context.cv_repo.get_by_id(cv_id)
            if not cv:
                return AgentResult.fail(f"CV not found: {cv_id}", self.name)
        
        try:
            # Generate embeddings if chunks provided
            chunks_stored = 0
            if chunks:
                chunks_stored = await self.embedding_tools.store(cv_id, chunks)
                self._logger.debug(f"Stored {chunks_stored} embeddings")
            
            # Get evaluation template
            template = None
            if template_id:
                template = await self.context.template_repo.get_with_criteria(template_id)
            
            if not template:
                template = await self.context.template_repo.get_default_template()
            
            if not template:
                return AgentResult.fail(
                    "No evaluation template available",
                    self.name,
                )
            
            criteria_list = template.criteria
            self._logger.debug(f"Using template: {template.name}")
            
            # Evaluate with LangChain
            evaluation = await self.evaluation_tools.evaluate(
                cv_text=cv_text,
                template=template,
                criteria_list=criteria_list,
            )
            
            self._logger.info(
                f"Evaluation complete: {evaluation.percentage}%, "
                f"passed={evaluation.passed}"
            )
            
            # Store evaluation results
            status = EvaluationStatus.PASS if evaluation.passed else EvaluationStatus.FAIL
            criteria_results = format_criteria_results(evaluation)
            
            db_evaluation = CVEvaluation(
                cv_id=cv_id,
                template_id=template.id,
                score=int(evaluation.percentage),
                status=status.value,
                reasoning=evaluation.summary,
                criteria_results=criteria_results,
            )
            db_evaluation = await self.context.evaluation_repo.create(db_evaluation)
            
            # Update CV status
            cv.status = CVStatus.EVALUATED.value
            if candidate_name and not cv.candidate_name:
                cv.candidate_name = candidate_name
            await self.context.cv_repo.update(cv)
            
            await self.context.session.commit()
            
            return AgentResult.ok(
                data={
                    "cv_id": str(cv_id),
                    "evaluation_id": str(db_evaluation.id),
                    "score": evaluation.percentage,
                    "passed": evaluation.passed,
                    "summary": evaluation.summary,
                    "criteria_results": criteria_results,
                    "chunks_stored": chunks_stored,
                },
                agent_name=self.name,
                next_task=TaskType.CHECK_THRESHOLD,  # Chain to notification check
            )
            
        except Exception as e:
            # Mark CV as error
            self._logger.error(f"Evaluation failed: {e}")
            cv.status = CVStatus.ERROR.value
            await self.context.cv_repo.update(cv)
            await self.context.session.commit()
            raise
    
    async def _generate_embeddings(self, message: AgentMessage) -> AgentResult:
        """Generate and store embeddings for CV chunks.
        
        Args:
            message: AgentMessage with cv_id and chunks.
        
        Returns:
            AgentResult with count of stored embeddings.
        """
        cv_id = message.cv_id or message.payload.get("cv_id")
        chunks = message.payload.get("chunks", [])
        
        if not cv_id:
            return AgentResult.fail("Missing cv_id", self.name)
        if not chunks:
            return AgentResult.fail("Missing chunks in payload", self.name)
        
        # Convert string to UUID if needed
        if isinstance(cv_id, str):
            cv_id = uuid.UUID(cv_id)
        
        self._logger.info(f"Generating embeddings for CV: {cv_id}")
        
        chunks_stored = await self.embedding_tools.store(cv_id, chunks)
        
        return AgentResult.ok(
            data={
                "cv_id": str(cv_id),
                "chunks_stored": chunks_stored,
            },
            agent_name=self.name,
        )
    
    async def _re_evaluate(self, message: AgentMessage) -> AgentResult:
        """Re-evaluate an existing CV.
        
        Fetches the CV text from the database and runs evaluation
        again with the current template.
        
        Args:
            message: AgentMessage with cv_id.
        
        Returns:
            AgentResult with new evaluation results.
        """
        cv_id = message.cv_id or message.payload.get("cv_id")
        user_id = message.user_id
        template_id = message.payload.get("template_id")
        
        if not cv_id:
            return AgentResult.fail("Missing cv_id", self.name)
        
        # Convert string to UUID if needed
        if isinstance(cv_id, str):
            cv_id = uuid.UUID(cv_id)
        
        # Get CV
        cv = await self.context.cv_repo.get_by_id(cv_id)
        if not cv:
            return AgentResult.fail(f"CV not found: {cv_id}", self.name)
        
        # Verify ownership
        if user_id and cv.user_id != user_id:
            return AgentResult.fail("Access denied", self.name)
        
        self._logger.info(f"Re-evaluating CV: {cv_id}")
        
        # Update CV status
        cv.status = CVStatus.PROCESSING.value
        await self.context.cv_repo.update(cv)
        
        # Create new message with CV text
        eval_message = AgentMessage(
            task_type=TaskType.EVALUATE_CV,
            payload={
                "cv_text": cv.original_text,
                "cv_id": cv_id,
                "template_id": template_id,
            },
            metadata=message.metadata,
        )
        
        return await self._evaluate_cv(eval_message)
