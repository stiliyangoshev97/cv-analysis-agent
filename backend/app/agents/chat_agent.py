"""Chat Agent for RAG-powered conversations.

This agent handles conversational tasks about CVs using RAG
(Retrieval-Augmented Generation) with vector embeddings.

Tasks:
    ASK_QUESTION: Answer a question about a CV.
    EXPLAIN_SCORE: Explain a specific criterion score.
    COMPARE_CVS: Compare multiple CVs.
    GET_CHAT_HISTORY: Retrieve chat history.
    CLEAR_CHAT_HISTORY: Clear chat history.

Example:
    Using the chat agent::
    
        agent = ChatAgent(context)
        result = await agent.execute(AgentMessage(
            task_type=TaskType.ASK_QUESTION,
            payload={"question": "What's their Python experience?"},
            metadata={"cv_id": uuid, "user_id": uuid}
        ))
"""

import logging
import uuid
from typing import Set, List, Optional

from app.db.models.chat import ChatHistory, ChatRole

from .base import BaseAgent, AgentContext
from .messages import AgentMessage, AgentResult, TaskType
from .tools import EmbeddingTools, ConversationTools

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """Agent for RAG-powered CV conversations.
    
    Handles Q&A about CVs using vector similarity search to
    retrieve relevant context and LangChain for response generation.
    
    Supported Tasks:
        - ASK_QUESTION: Answer questions about a CV
        - EXPLAIN_SCORE: Explain criterion scores
        - COMPARE_CVS: Compare multiple CVs
        - GET_CHAT_HISTORY: Retrieve chat history
        - CLEAR_CHAT_HISTORY: Clear chat history
    
    Example:
        >>> agent = ChatAgent(context)
        >>> result = await agent.execute(AgentMessage(
        ...     task_type=TaskType.ASK_QUESTION,
        ...     payload={"question": "What's their experience?"},
        ...     metadata={"cv_id": cv_id, "user_id": user_id}
        ... ))
    """
    
    name = "chat_agent"
    supported_tasks: Set[TaskType] = {
        TaskType.ASK_QUESTION,
        TaskType.EXPLAIN_SCORE,
        TaskType.COMPARE_CVS,
        TaskType.GET_CHAT_HISTORY,
        TaskType.CLEAR_CHAT_HISTORY,
    }
    
    def __init__(self, context: AgentContext) -> None:
        """Initialize chat agent.
        
        Args:
            context: Shared AgentContext with repositories.
        """
        super().__init__(context)
        self.embedding_tools = EmbeddingTools(context.session)
        self.conversation_tools = ConversationTools(context.session)
    
    async def process(self, message: AgentMessage) -> AgentResult:
        """Process a chat task.
        
        Routes to appropriate handler based on task type.
        
        Args:
            message: AgentMessage with chat data.
        
        Returns:
            AgentResult with response or data.
        """
        if message.task_type == TaskType.ASK_QUESTION:
            return await self._ask_question(message)
        elif message.task_type == TaskType.EXPLAIN_SCORE:
            return await self._explain_score(message)
        elif message.task_type == TaskType.COMPARE_CVS:
            return await self._compare_cvs(message)
        elif message.task_type == TaskType.GET_CHAT_HISTORY:
            return await self._get_chat_history(message)
        elif message.task_type == TaskType.CLEAR_CHAT_HISTORY:
            return await self._clear_chat_history(message)
        else:
            return AgentResult.fail(
                f"Unknown task type: {message.task_type}",
                agent_name=self.name,
            )
    
    async def _verify_cv_access(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[AgentResult]:
        """Verify user has access to CV.
        
        Args:
            cv_id: UUID of the CV.
            user_id: UUID of the user.
        
        Returns:
            AgentResult with error if access denied, None if OK.
        """
        cv = await self.context.cv_repo.get_by_id(cv_id)
        if not cv:
            return AgentResult.fail(f"CV not found: {cv_id}", self.name)
        if cv.user_id != user_id:
            return AgentResult.fail("Access denied", self.name)
        return None
    
    async def _ask_question(self, message: AgentMessage) -> AgentResult:
        """Answer a question about a CV using RAG.
        
        1. Verifies CV access
        2. Retrieves relevant chunks via embedding search
        3. Gets conversation history
        4. Generates response with context
        5. Stores messages in history
        
        Args:
            message: AgentMessage with question, cv_id.
        
        Returns:
            AgentResult with response and sources.
        """
        cv_id = message.cv_id or message.payload.get("cv_id")
        user_id = message.user_id
        question = message.payload.get("question")
        
        if not cv_id:
            return AgentResult.fail("Missing cv_id", self.name)
        if not user_id:
            return AgentResult.fail("Missing user_id", self.name)
        if not question:
            return AgentResult.fail("Missing question in payload", self.name)
        
        # Convert strings to UUIDs
        if isinstance(cv_id, str):
            cv_id = uuid.UUID(cv_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        # Verify access
        access_error = await self._verify_cv_access(cv_id, user_id)
        if access_error:
            return access_error
        
        self._logger.info(f"Answering question for CV: {cv_id}")
        
        # Get CV
        cv = await self.context.cv_repo.get_by_id(cv_id)
        
        # Search for relevant chunks
        context_chunks = await self.embedding_tools.search(cv_id, question, k=5)
        
        # Get chat history
        history = await self.context.chat_repo.get_history(cv_id, user_id, limit=10)
        chat_messages = [
            {"role": msg.role, "content": msg.message}
            for msg in reversed(history)  # Oldest first
        ]
        
        # Generate response
        response = await self.conversation_tools.ask(
            question=question,
            cv_text=cv.original_text,
            context_chunks=context_chunks,
            chat_history=chat_messages,
        )
        
        # Store user message
        user_msg = ChatHistory(
            cv_id=cv_id,
            user_id=user_id,
            role=ChatRole.USER.value,
            message=question,
        )
        await self.context.chat_repo.create(user_msg)
        
        # Store assistant message
        assistant_msg = ChatHistory(
            cv_id=cv_id,
            user_id=user_id,
            role=ChatRole.ASSISTANT.value,
            message=response,
        )
        assistant_msg = await self.context.chat_repo.create(assistant_msg)
        
        await self.context.session.commit()
        
        return AgentResult.ok(
            data={
                "response": response,
                "message_id": str(assistant_msg.id),
                "sources_count": len(context_chunks),
            },
            agent_name=self.name,
        )
    
    async def _explain_score(self, message: AgentMessage) -> AgentResult:
        """Explain a specific criterion score.
        
        Args:
            message: AgentMessage with cv_id, criterion_name.
        
        Returns:
            AgentResult with detailed explanation.
        """
        cv_id = message.cv_id or message.payload.get("cv_id")
        user_id = message.user_id
        criterion_name = message.payload.get("criterion_name") or message.payload.get("criterion")
        
        if not cv_id:
            return AgentResult.fail("Missing cv_id", self.name)
        if not user_id:
            return AgentResult.fail("Missing user_id", self.name)
        if not criterion_name:
            return AgentResult.fail("Missing criterion_name in payload", self.name)
        
        # Convert strings to UUIDs
        if isinstance(cv_id, str):
            cv_id = uuid.UUID(cv_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        # Verify access
        access_error = await self._verify_cv_access(cv_id, user_id)
        if access_error:
            return access_error
        
        self._logger.info(f"Explaining {criterion_name} for CV: {cv_id}")
        
        # Get CV and evaluation
        cv = await self.context.cv_repo.get_by_id(cv_id)
        evaluation = await self.context.evaluation_repo.get_latest(cv_id)
        
        if not evaluation:
            return AgentResult.fail("No evaluation found for CV", self.name)
        
        # Get criterion from results
        criteria_results = evaluation.criteria_results or {}
        criterion = criteria_results.get(criterion_name)
        
        if not criterion:
            available = list(criteria_results.keys())
            return AgentResult.fail(
                f"Criterion '{criterion_name}' not found. "
                f"Available: {', '.join(available)}",
                self.name,
            )
        
        # Generate explanation
        explanation = await self.conversation_tools.explain_score(
            criterion_name=criterion_name,
            score=criterion.get("score", 0),
            max_score=criterion.get("max_score", 10),
            reasoning=criterion.get("reasoning", ""),
            evidence=criterion.get("evidence", ""),
            cv_text=cv.original_text,
        )
        
        return AgentResult.ok(
            data={
                "criterion": criterion_name,
                "score": criterion.get("score"),
                "max_score": criterion.get("max_score"),
                "explanation": explanation,
            },
            agent_name=self.name,
        )
    
    async def _compare_cvs(self, message: AgentMessage) -> AgentResult:
        """Compare multiple CVs.
        
        Args:
            message: AgentMessage with cv_ids list.
        
        Returns:
            AgentResult with comparison data.
        """
        cv_ids = message.payload.get("cv_ids", [])
        user_id = message.user_id
        criteria = message.payload.get("criteria", [])  # Optional specific criteria
        
        if not user_id:
            return AgentResult.fail("Missing user_id", self.name)
        if len(cv_ids) < 2:
            return AgentResult.fail("At least 2 CVs required for comparison", self.name)
        if len(cv_ids) > 5:
            return AgentResult.fail("Maximum 5 CVs for comparison", self.name)
        
        # Convert strings to UUIDs
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        cv_uuids = [uuid.UUID(cid) if isinstance(cid, str) else cid for cid in cv_ids]
        
        self._logger.info(f"Comparing {len(cv_uuids)} CVs")
        
        # Gather CV data
        comparison_data = []
        for cv_id in cv_uuids:
            # Verify access
            cv = await self.context.cv_repo.get_by_id(cv_id)
            if not cv:
                return AgentResult.fail(f"CV not found: {cv_id}", self.name)
            if cv.user_id != user_id:
                return AgentResult.fail(f"Access denied for CV: {cv_id}", self.name)
            
            # Get evaluation
            evaluation = await self.context.evaluation_repo.get_latest(cv_id)
            
            comparison_data.append({
                "cv_id": str(cv_id),
                "filename": cv.filename,
                "candidate_name": cv.candidate_name,
                "score": evaluation.score if evaluation else None,
                "status": evaluation.status if evaluation else None,
                "criteria_results": evaluation.criteria_results if evaluation else {},
            })
        
        # Sort by score (highest first)
        comparison_data.sort(
            key=lambda x: x.get("score") or 0,
            reverse=True
        )
        
        # Build ranking
        for i, item in enumerate(comparison_data):
            item["rank"] = i + 1
        
        return AgentResult.ok(
            data={
                "count": len(comparison_data),
                "comparison": comparison_data,
            },
            agent_name=self.name,
        )
    
    async def _get_chat_history(self, message: AgentMessage) -> AgentResult:
        """Retrieve chat history for a CV.
        
        Args:
            message: AgentMessage with cv_id.
        
        Returns:
            AgentResult with chat messages.
        """
        cv_id = message.cv_id or message.payload.get("cv_id")
        user_id = message.user_id
        limit = message.payload.get("limit", 50)
        
        if not cv_id:
            return AgentResult.fail("Missing cv_id", self.name)
        if not user_id:
            return AgentResult.fail("Missing user_id", self.name)
        
        # Convert strings to UUIDs
        if isinstance(cv_id, str):
            cv_id = uuid.UUID(cv_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        # Verify access
        access_error = await self._verify_cv_access(cv_id, user_id)
        if access_error:
            return access_error
        
        # Get history
        history = await self.context.chat_repo.get_history(cv_id, user_id, limit=limit)
        
        messages = [
            {
                "id": str(msg.id),
                "role": msg.role,
                "message": msg.message,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in reversed(history)  # Oldest first
        ]
        
        return AgentResult.ok(
            data={
                "cv_id": str(cv_id),
                "count": len(messages),
                "messages": messages,
            },
            agent_name=self.name,
        )
    
    async def _clear_chat_history(self, message: AgentMessage) -> AgentResult:
        """Clear chat history for a CV.
        
        Args:
            message: AgentMessage with cv_id.
        
        Returns:
            AgentResult with count of deleted messages.
        """
        cv_id = message.cv_id or message.payload.get("cv_id")
        user_id = message.user_id
        
        if not cv_id:
            return AgentResult.fail("Missing cv_id", self.name)
        if not user_id:
            return AgentResult.fail("Missing user_id", self.name)
        
        # Convert strings to UUIDs
        if isinstance(cv_id, str):
            cv_id = uuid.UUID(cv_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        # Verify access
        access_error = await self._verify_cv_access(cv_id, user_id)
        if access_error:
            return access_error
        
        self._logger.info(f"Clearing chat history for CV: {cv_id}")
        
        # Clear history
        deleted = await self.context.chat_repo.clear_history(cv_id, user_id)
        await self.context.session.commit()
        
        return AgentResult.ok(
            data={
                "cv_id": str(cv_id),
                "deleted_count": deleted,
            },
            agent_name=self.name,
        )
