"""Chat service for RAG-powered CV conversations.

This module provides the ChatService class for orchestrating
RAG (Retrieval-Augmented Generation) conversations about CVs.

The service:
1. Verifies CV ownership
2. Retrieves relevant CV chunks via embeddings
3. Gets conversation history
4. Generates AI responses with context
5. Persists chat messages

Classes:
    ChatService: Orchestration service for RAG chat.

Example:
    Using the service::
    
        service = ChatService(session)
        response = await service.ask(
            cv_id=cv_id,
            user_id=user_id,
            question="What is their Python experience?"
        )
"""

import uuid
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cv import CV, CVEvaluation
from app.db.models.chat import ChatHistory, ChatRole
from app.features.cv.cv_repository import CVRepository
from app.features.cv.evaluation_repository import EvaluationRepository
from app.features.cv.embedding_repository import EmbeddingRepository
from app.langchain.chains.conversation_chain import (
    ConversationChain,
    ExplanationChain,
    ChatMessage,
)
from app.features.settings.user_keys_service import UserKeysService
from app.langchain.config import get_llm
from .chat_repository import ChatRepository


@dataclass
class ChatResult:
    """Result from a chat interaction.
    
    Attributes:
        message: The assistant's response as a ChatHistory entity.
        sources: CV chunks used as context.
        sources_count: Number of chunks retrieved.
    """
    message: ChatHistory
    sources: List[str]
    sources_count: int


class ChatService:
    """Orchestration service for RAG-powered CV chat.
    
    Combines repositories and LangChain components to provide
    conversational Q&A about CVs with vector-based context retrieval.
    
    Attributes:
        session: AsyncSession for database operations.
        cv_repo: Repository for CV operations.
        evaluation_repo: Repository for evaluation operations.
        embedding_repo: Repository for embedding operations.
        chat_repo: Repository for chat history operations.
        conversation_chain: LangChain chain for RAG responses.
        explanation_chain: LangChain chain for score explanations.
    
    Example:
        >>> service = ChatService(session)
        >>> result = await service.ask(cv_id, user_id, "What's their experience?")
        >>> print(result.message.message)
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
        
        # Initialize repositories
        self.cv_repo = CVRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
        self.embedding_repo = EmbeddingRepository(session)
        self.chat_repo = ChatRepository(session)
        
        # Initialize user keys service
        self.user_keys_service = UserKeysService(session)
        
        # LangChain components are created per-request with user keys
        # self.conversation_chain and self.explanation_chain are created dynamically
    
    async def _verify_cv_ownership(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CV:
        """Verify CV exists and belongs to user.
        
        Args:
            cv_id: CV's UUID.
            user_id: User's UUID.
        
        Returns:
            CV entity if valid.
        
        Raises:
            ValueError: If CV not found or doesn't belong to user.
        """
        cv = await self.cv_repo.get_by_id(cv_id)
        
        if not cv:
            raise ValueError(f"CV not found: {cv_id}")
        
        if cv.user_id != user_id:
            raise ValueError("You don't have access to this CV")
        
        return cv
    
    async def _get_conversation_history(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
        limit: int = 10,
    ) -> List[ChatMessage]:
        """Get recent conversation history as ChatMessage list.
        
        Converts ChatHistory entities to LangChain ChatMessage format.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            limit: Max messages to retrieve.
        
        Returns:
            List of ChatMessage for LangChain.
        """
        history = await self.chat_repo.get_recent_messages(user_id, cv_id, limit)
        
        return [
            ChatMessage(
                role="user" if msg.role == ChatRole.USER.value else "assistant",
                content=msg.message,
            )
            for msg in history
        ]
    
    async def _get_evaluation_summary(
        self,
        cv_id: uuid.UUID,
    ) -> Optional[str]:
        """Get evaluation summary for context.
        
        Args:
            cv_id: CV's UUID.
        
        Returns:
            Formatted evaluation summary or None.
        """
        evaluation = await self.evaluation_repo.get_latest_by_cv(cv_id)
        
        if not evaluation:
            return None
        
        # Format evaluation summary
        passed = evaluation.status.lower() == "pass"
        summary_parts = [
            f"Overall Score: {evaluation.score}/100",
            f"Status: {'PASS' if passed else 'FAIL'}",
            f"Reasoning: {evaluation.reasoning or 'N/A'}",
        ]
        
        # Add criteria scores if available
        if evaluation.criteria_results:
            summary_parts.append("\nCriteria Scores:")
            # Handle both dict format (name -> data) and list format ([{name, score}])
            criteria = evaluation.criteria_results
            if isinstance(criteria, dict):
                # Dict format: {"Technical Skills": {"score": 20, "max_score": 25}}
                for name, data in criteria.items():
                    if isinstance(data, dict):
                        score = data.get("score", 0)
                        max_score = data.get("max_score", 0)
                        summary_parts.append(f"  - {name}: {score}/{max_score}")
            elif isinstance(criteria, list):
                # List format: [{"name": "Technical Skills", "score": 20, "max_score": 25}]
                for criterion in criteria:
                    name = criterion.get("name", "Unknown")
                    score = criterion.get("score", 0)
                    max_score = criterion.get("max_score", 0)
                    summary_parts.append(f"  - {name}: {score}/{max_score}")
        
        return "\n".join(summary_parts)
    
    async def ask(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        question: str,
    ) -> ChatResult:
        """Ask a question about a CV.
        
        Full RAG pipeline:
        1. Verify CV ownership
        2. Get user's API keys
        3. Save user's question
        4. Get conversation history
        5. Get evaluation summary
        6. Generate AI response with context (using user's LLM key)
        7. Save assistant's response
        8. Return result with sources
        
        Args:
            cv_id: UUID of the CV to query.
            user_id: UUID of the user asking.
            question: The user's question.
        
        Returns:
            ChatResult with response and metadata.
        
        Raises:
            ValueError: If CV not found, access denied, or API keys not configured.
        """
        # 1. Verify ownership
        cv = await self._verify_cv_ownership(cv_id, user_id)
        
        # 2. Get user's API keys
        user_keys = await self.user_keys_service.validate_keys_for_cv_processing(user_id)
        
        # Create LLM with user's key
        llm = get_llm(
            provider=user_keys.default_provider,
            api_key=user_keys.get_llm_key(),
        )
        
        # Create conversation chain with user's LLM and OpenAI key for embeddings
        conversation_chain = ConversationChain(
            self.session, 
            llm=llm,
            openai_api_key=user_keys.openai_key,
        )
        
        # 3. Save user's question
        await self.chat_repo.add_user_message(user_id, cv_id, question)
        
        # 4. Get conversation history (before the new question)
        history = await self._get_conversation_history(user_id, cv_id)
        
        # 5. Get evaluation summary
        eval_summary = await self._get_evaluation_summary(cv_id)
        
        # 6. Generate AI response (using user's LLM key)
        response = await conversation_chain.ask(
            cv_id=cv_id,
            question=question,
            chat_history=history,
            evaluation_summary=eval_summary,
        )
        
        # 6. Save assistant's response
        assistant_msg = await self.chat_repo.add_assistant_message(
            user_id, cv_id, response.content
        )
        
        # 7. Get sources (chunks used)
        # Note: We could enhance ConversationChain to return sources
        sources = await self._get_relevant_chunks(
            cv_id, 
            question,
            api_key=user_keys.openai_key,
        )
        
        return ChatResult(
            message=assistant_msg,
            sources=sources,
            sources_count=len(sources),
        )
    
    async def _get_relevant_chunks(
        self,
        cv_id: uuid.UUID,
        query: str,
        limit: int = 3,
        api_key: str | None = None,
    ) -> List[str]:
        """Get relevant CV chunks for a query.
        
        Used to show sources in the response.
        
        Args:
            cv_id: CV's UUID.
            query: Query to search for.
            limit: Max chunks to return.
            api_key: User's OpenAI API key for embeddings.
        
        Returns:
            List of chunk text excerpts.
        """
        from app.langchain.embeddings import EmbeddingService
        
        embedding_service = EmbeddingService(self.session, api_key=api_key)
        chunks = await embedding_service.search_similar(
            cv_id=cv_id,
            query=query,
            limit=limit,
        )
        
        return [chunk.chunk_text[:200] + "..." for chunk in chunks]
    
    async def get_history(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: Optional[int] = None,
    ) -> List[ChatHistory]:
        """Get chat history for a CV.
        
        Args:
            cv_id: CV's UUID.
            user_id: User's UUID.
            limit: Optional message limit.
        
        Returns:
            List of ChatHistory messages.
        
        Raises:
            ValueError: If CV not found or access denied.
        """
        # Verify ownership
        await self._verify_cv_ownership(cv_id, user_id)
        
        return await self.chat_repo.get_conversation(user_id, cv_id, limit)
    
    async def clear_history(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> int:
        """Clear chat history for a CV.
        
        Args:
            cv_id: CV's UUID.
            user_id: User's UUID.
        
        Returns:
            Number of messages deleted.
        
        Raises:
            ValueError: If CV not found or access denied.
        """
        # Verify ownership
        await self._verify_cv_ownership(cv_id, user_id)
        
        return await self.chat_repo.clear_conversation(user_id, cv_id)
    
    async def explain_criterion(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        criterion_name: str,
    ) -> dict:
        """Explain a specific criterion score.
        
        Retrieves the evaluation and generates a detailed explanation
        for why the candidate received a particular score.
        
        Args:
            cv_id: CV's UUID.
            user_id: User's UUID.
            criterion_name: Name of the criterion to explain.
        
        Returns:
            Dict with criterion, score, max_score, explanation, evidence.
        
        Raises:
            ValueError: If CV not found, access denied, or criterion not found.
        """
        # Verify ownership
        cv = await self._verify_cv_ownership(cv_id, user_id)
        
        # Get user's API keys
        user_keys = await self.user_keys_service.validate_keys_for_cv_processing(user_id)
        
        # Create LLM with user's key
        llm = get_llm(
            provider=user_keys.default_provider,
            api_key=user_keys.get_llm_key(),
        )
        
        # Create explanation chain with user's LLM
        explanation_chain = ExplanationChain(llm=llm)
        
        # Get evaluation
        evaluation = await self.evaluation_repo.get_latest_by_cv(cv_id)
        if not evaluation:
            raise ValueError("No evaluation found for this CV")
        
        # Find the criterion - handle both dict and list formats
        criterion_data = None
        criterion_actual_name = criterion_name
        available_criteria = []
        
        if evaluation.criteria_results:
            criteria = evaluation.criteria_results
            if isinstance(criteria, dict):
                # Dict format: {"Technical Skills": {"score": 20, "max_score": 25}}
                for name, data in criteria.items():
                    available_criteria.append(name)
                    if name.lower() == criterion_name.lower():
                        criterion_data = data
                        criterion_data["name"] = name  # Add name to data
                        criterion_actual_name = name
                        break
            elif isinstance(criteria, list):
                # List format: [{"name": "Technical Skills", "score": 20, "max_score": 25}]
                for criterion in criteria:
                    crit_name = criterion.get("name", "")
                    available_criteria.append(crit_name)
                    if crit_name.lower() == criterion_name.lower():
                        criterion_data = criterion
                        criterion_actual_name = crit_name
                        break
        
        if not criterion_data:
            raise ValueError(
                f"Criterion '{criterion_name}' not found. "
                f"Available: {', '.join(available_criteria)}"
            )
        
        # Generate explanation
        score = criterion_data.get("score", 0)
        max_score = criterion_data.get("max_score", 0)
        reasoning = criterion_data.get("reasoning", "No reasoning available")
        
        explanation = await explanation_chain.explain(
            cv_text=cv.original_text or "",
            criterion_name=criterion_name,
            score=score,
            max_score=max_score,
            reasoning=reasoning,
        )
        
        # Get evidence (relevant chunks)
        evidence = await self._get_relevant_chunks(cv_id, criterion_name)
        
        return {
            "criterion": criterion_actual_name,
            "score": score,
            "max_score": max_score,
            "explanation": explanation,
            "evidence": evidence,
        }
    
    async def compare_cvs(
        self,
        cv_ids: List[uuid.UUID],
        user_id: uuid.UUID,
        question: str = "Compare these candidates overall",
    ) -> dict:
        """Compare multiple CVs.
        
        Retrieves relevant information from each CV and generates
        a comparison analysis.
        
        Args:
            cv_ids: List of CV UUIDs to compare (2-5).
            user_id: User's UUID.
            question: Comparison focus/question.
        
        Returns:
            Dict with cv_ids, comparison analysis, and optional ranking.
        
        Raises:
            ValueError: If any CV not found or access denied.
        """
        if len(cv_ids) < 2 or len(cv_ids) > 5:
            raise ValueError("Must compare between 2 and 5 CVs")
        
        # Get user's API keys
        user_keys = await self.user_keys_service.validate_keys_for_cv_processing(user_id)
        
        # Verify all CVs belong to user
        cvs = []
        for cv_id in cv_ids:
            cv = await self._verify_cv_ownership(cv_id, user_id)
            cvs.append(cv)
        
        # Build context from all CVs
        context_parts = []
        for cv in cvs:
            # Get candidate name and summary
            name = cv.candidate_name or cv.filename
            
            # Get evaluation summary
            evaluation = await self.evaluation_repo.get_latest_by_cv(cv.id)
            eval_info = ""
            if evaluation:
                eval_info = f" (Score: {evaluation.score}/100)"
            
            # Get relevant chunks for the comparison question
            chunks = await self._get_relevant_chunks(cv.id, question, limit=2)
            chunks_text = "\n".join(chunks) if chunks else "No detailed content available."
            
            context_parts.append(
                f"## Candidate: {name}{eval_info}\n{chunks_text}"
            )
        
        combined_context = "\n\n".join(context_parts)
        
        # Generate comparison using conversation chain
        # Use a special prompt for comparison
        comparison_question = f"""Compare these candidates:

{combined_context}

Question: {question}

Please provide:
1. Key differences between candidates
2. Strengths and weaknesses of each
3. Recommendation on which candidate might be best (with caveats)"""
        
        # Use the LLM directly for comparison (no single CV context, using user's key)
        llm = get_llm(
            provider=user_keys.default_provider,
            api_key=user_keys.get_llm_key(),
            temperature=0.3,
        )
        
        response = await llm.ainvoke(comparison_question)
        
        return {
            "cv_ids": cv_ids,
            "comparison": response.content,
            "ranking": None,  # Could parse from response if needed
        }
