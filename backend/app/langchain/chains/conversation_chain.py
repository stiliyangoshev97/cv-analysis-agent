"""
RAG Conversation Chain

LangChain chain for answering questions about CVs using RAG.
Retrieves relevant CV chunks and generates context-aware responses.
"""

import uuid
from datetime import datetime
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.langchain.config import get_llm
from app.langchain.embeddings import EmbeddingService


class ChatMessage(BaseModel):
    """A single chat message.
    
    Attributes:
        role: Message sender (user or assistant).
        content: Message text content.
        timestamp: When the message was sent.
    """
    role: Literal["user", "assistant"] = Field(description="Message sender")
    content: str = Field(description="Message text content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# System prompt for CV Q&A
CONVERSATION_SYSTEM_PROMPT = """You are a helpful CV analysis assistant.

You help hiring managers and recruiters understand candidate CVs by answering questions
about their qualifications, experience, and fit for roles.

**Your Capabilities:**
- Explain specific aspects of a candidate's background
- Clarify why certain scores were given in evaluations
- Compare qualifications against job requirements
- Highlight relevant experience or skills
- Identify potential concerns or gaps

**Guidelines:**
1. Base your answers on the CV content provided in the context
2. If information isn't in the CV, say so clearly
3. Be objective and fair in your assessments
4. Support your points with specific evidence from the CV
5. Keep responses concise but thorough

**Context from CV:**
{cv_context}

**Evaluation Summary (if available):**
{evaluation_context}"""

CONVERSATION_HUMAN_PROMPT = """{question}"""


class ConversationChain:
    """
    RAG-powered conversation chain for CV Q&A.
    
    Retrieves relevant CV chunks based on the question, then generates
    an informed response using that context.
    
    Example:
        ```python
        chain = ConversationChain(session)
        
        # Simple question
        response = await chain.ask(
            cv_id=cv.id,
            question="What is their React experience?"
        )
        print(response.content)
        
        # With conversation history
        history = [
            ChatMessage(role="user", content="What's their background?"),
            ChatMessage(role="assistant", content="They have 5 years..."),
        ]
        response = await chain.ask(
            cv_id=cv.id,
            question="Tell me more about their fintech work",
            chat_history=history
        )
        ```
    """
    
    def __init__(
        self,
        session: AsyncSession,
        llm: ChatAnthropic | None = None,
        num_chunks: int = 5,
    ):
        """
        Initialize the conversation chain.
        
        Args:
            session: Database session for embedding retrieval.
            llm: Optional pre-configured LLM instance.
            num_chunks: Number of relevant chunks to retrieve per question.
        """
        self.session = session
        self.llm = llm or get_llm(temperature=0.3)  # Slightly more creative for chat
        self.embedding_service = EmbeddingService(session)
        self.num_chunks = num_chunks
        
        # Build the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CONVERSATION_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", CONVERSATION_HUMAN_PROMPT),
        ])
    
    async def _retrieve_context(
        self,
        cv_id: uuid.UUID,
        question: str,
    ) -> str:
        """Retrieve relevant CV chunks for the question."""
        chunks = await self.embedding_service.search_similar(
            cv_id=cv_id,
            query=question,
            limit=self.num_chunks,
        )
        
        if not chunks:
            return "No CV content available."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Excerpt {i}]\n{chunk.chunk_text}")
        
        return "\n\n".join(context_parts)
    
    def _format_history(
        self,
        chat_history: list[ChatMessage] | None,
    ) -> list[HumanMessage | AIMessage]:
        """Convert ChatMessage list to LangChain message format."""
        if not chat_history:
            return []
        
        messages = []
        for msg in chat_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        
        return messages
    
    async def ask(
        self,
        cv_id: uuid.UUID,
        question: str,
        chat_history: list[ChatMessage] | None = None,
        evaluation_summary: str | None = None,
    ) -> ChatMessage:
        """
        Ask a question about a CV.
        
        Args:
            cv_id: UUID of the CV to query.
            question: The user's question.
            chat_history: Previous messages in the conversation.
            evaluation_summary: Optional evaluation summary for context.
        
        Returns:
            ChatMessage with the assistant's response.
        
        Example:
            ```python
            response = await chain.ask(
                cv_id=cv.id,
                question="Why did they score low on fintech experience?"
            )
            print(response.content)
            ```
        """
        # Retrieve relevant CV context
        cv_context = await self._retrieve_context(cv_id, question)
        
        # Format evaluation context
        evaluation_context = evaluation_summary or "No evaluation available."
        
        # Format chat history
        history_messages = self._format_history(chat_history)
        
        # Build and run the chain
        chain = self.prompt | self.llm
        
        response = await chain.ainvoke({
            "cv_context": cv_context,
            "evaluation_context": evaluation_context,
            "chat_history": history_messages,
            "question": question,
        })
        
        return ChatMessage(
            role="assistant",
            content=response.content,
        )
    
    async def explain_score(
        self,
        cv_id: uuid.UUID,
        criterion_name: str,
        score: int,
        max_score: int,
        reasoning: str,
    ) -> ChatMessage:
        """
        Generate a detailed explanation for a criterion score.
        
        Specialized method for the "Why?" feature on evaluation results.
        
        Args:
            cv_id: UUID of the CV.
            criterion_name: Name of the criterion.
            score: Actual score received.
            max_score: Maximum possible score.
            reasoning: Original reasoning from evaluation.
        
        Returns:
            ChatMessage with detailed explanation.
        """
        question = f"""I want to understand the score for "{criterion_name}".

The candidate received {score}/{max_score} points.

Original evaluation reasoning: {reasoning}

Can you explain in more detail:
1. What specific evidence from the CV led to this score?
2. What would the candidate need to score higher?
3. Is this score reasonable given the CV content?"""
        
        return await self.ask(
            cv_id=cv_id,
            question=question,
        )
    
    async def compare_to_requirements(
        self,
        cv_id: uuid.UUID,
        job_requirements: str,
    ) -> ChatMessage:
        """
        Compare a CV against specific job requirements.
        
        Args:
            cv_id: UUID of the CV.
            job_requirements: Text describing job requirements.
        
        Returns:
            ChatMessage with comparison analysis.
        """
        question = f"""Compare this candidate's qualifications against these job requirements:

{job_requirements}

Please provide:
1. Requirements clearly met
2. Requirements partially met
3. Requirements not met or unclear
4. Overall fit assessment (Strong Fit / Good Fit / Partial Fit / Poor Fit)"""
        
        return await self.ask(cv_id=cv_id, question=question)


class ExplanationChain:
    """
    Specialized chain for generating evaluation explanations.
    
    Used when users click "Why?" on a specific score to get
    a detailed breakdown of the reasoning.
    
    Example:
        ```python
        chain = ExplanationChain()
        
        explanation = await chain.explain(
            cv_text=cv.original_text,
            criterion_name="Technical Skills",
            score=18,
            max_score=30,
            reasoning="Limited evidence of required skills"
        )
        print(explanation)
        ```
    """
    
    EXPLANATION_PROMPT = """You are explaining a CV evaluation score to a hiring manager.

## Criterion: {criterion_name}
## Score: {score}/{max_score} ({percentage:.1f}%)
## Original Reasoning: {reasoning}

## Relevant CV Excerpts:
{cv_excerpts}

Please provide a detailed, educational explanation:

1. **Score Breakdown**: Why did this CV receive {score} out of {max_score} points?

2. **Evidence Analysis**: What specific elements from the CV support this score?

3. **Gap Analysis**: What would the candidate need to demonstrate to score higher?

4. **Fair Assessment**: Is this score fair and consistent? Any caveats?

Keep your explanation clear and professional."""
    
    def __init__(self, llm: ChatAnthropic | None = None):
        self.llm = llm or get_llm(temperature=0.2)
        self.prompt = ChatPromptTemplate.from_template(self.EXPLANATION_PROMPT)
        self.chain = self.prompt | self.llm
    
    async def explain(
        self,
        cv_text: str,
        criterion_name: str,
        score: int,
        max_score: int,
        reasoning: str,
    ) -> str:
        """
        Generate detailed explanation for a score.
        
        Args:
            cv_text: Full CV text (or relevant excerpts).
            criterion_name: Name of the criterion.
            score: Actual score received.
            max_score: Maximum possible score.
            reasoning: Original reasoning from evaluation.
        
        Returns:
            Detailed explanation string.
        """
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        # Use first 2000 chars of CV as context (or could use embeddings)
        cv_excerpts = cv_text[:2000] + ("..." if len(cv_text) > 2000 else "")
        
        response = await self.chain.ainvoke({
            "criterion_name": criterion_name,
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "reasoning": reasoning,
            "cv_excerpts": cv_excerpts,
        })
        
        return response.content
