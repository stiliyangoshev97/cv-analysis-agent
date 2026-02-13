"""Shared tools and utilities for agents.

This module provides common utilities used across multiple agents,
including document processing helpers, validation functions, and
integration with LangChain components.

Functions:
    validate_file: Validate uploaded file content and type.
    extract_candidate_name: Extract candidate name from CV text.
    format_criteria_results: Format evaluation criteria for storage.

Classes:
    DocumentTools: LangChain document processing utilities.
    EmbeddingTools: Embedding generation and retrieval utilities.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.langchain.document_processor import DocumentProcessor, ProcessedDocument
from app.langchain.embeddings import EmbeddingService
from app.langchain.chains.evaluation_chain import (
    EvaluationChain,
    CVEvaluationResult,
    get_evaluation_chain,
)
from app.langchain.chains.conversation_chain import (
    ConversationChain,
    ExplanationChain,
    ChatMessage,
)

logger = logging.getLogger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc"}


def validate_file(file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """Validate uploaded file content and type.
    
    Checks:
    1. File extension is supported (.pdf, .docx, .doc)
    2. File content is not empty
    3. File size is within limits (10MB)
    
    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename.
    
    Returns:
        Tuple of (is_valid, error_message).
        If valid: (True, None)
        If invalid: (False, "Error description")
    
    Example:
        >>> is_valid, error = validate_file(pdf_bytes, "resume.pdf")
        >>> if not is_valid:
        ...     raise ValueError(error)
    """
    # Check filename
    if not filename:
        return False, "Filename is required"
    
    # Check extension
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
    
    # Check content
    if not file_content:
        return False, "File content is empty"
    
    # Check size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_content) > max_size:
        return False, f"File too large: {len(file_content)} bytes. Max: {max_size} bytes"
    
    return True, None


def extract_candidate_name(cv_text: str) -> Optional[str]:
    """Extract candidate name from CV text.
    
    Uses simple heuristics to find the candidate's name,
    typically found at the beginning of the document.
    
    Args:
        cv_text: Full text of the CV.
    
    Returns:
        Extracted name or None if not found.
    
    Note:
        This is a simple implementation. Could be enhanced with
        NLP or a dedicated LLM call for better accuracy.
    """
    if not cv_text:
        return None
    
    # Take first few lines
    lines = cv_text.strip().split("\n")[:5]
    
    for line in lines:
        line = line.strip()
        # Skip empty lines and common headers
        if not line or len(line) < 3:
            continue
        
        # Skip lines that look like headers/titles
        lower = line.lower()
        if any(header in lower for header in [
            "curriculum vitae", "resume", "cv", "profile",
            "email", "phone", "address", "linkedin"
        ]):
            continue
        
        # Likely a name if it's 2-4 words with capital letters
        words = line.split()
        if 2 <= len(words) <= 4:
            # Check if words look like names (capitalized)
            if all(w[0].isupper() for w in words if w):
                return line
    
    return None


def format_criteria_results(evaluation: CVEvaluationResult) -> dict:
    """Format evaluation criteria results for database storage.
    
    Converts the CVEvaluationResult criteria scores into a
    dictionary format suitable for JSON storage.
    
    Args:
        evaluation: The evaluation result from LangChain.
    
    Returns:
        Dictionary mapping criterion names to score details.
    
    Example:
        >>> criteria = format_criteria_results(evaluation)
        >>> print(criteria["python"]["score"])  # 8
        >>> print(criteria["python"]["reasoning"])  # "Strong experience..."
    """
    return {
        score.name: {
            "score": score.score,
            "max_score": score.max_score,
            "reasoning": score.reasoning,
            "evidence": score.evidence,
        }
        for score in evaluation.criteria_scores
    }


@dataclass
class DocumentTools:
    """Document processing utilities using LangChain.
    
    Provides methods for parsing PDF/DOCX files and extracting
    structured content using LangChain's document loaders.
    
    Attributes:
        processor: LangChain DocumentProcessor instance.
    
    Example:
        >>> tools = DocumentTools()
        >>> doc = await tools.process(pdf_bytes, "resume.pdf")
        >>> print(f"Extracted {len(doc.full_text)} characters")
    """
    
    def __init__(self) -> None:
        """Initialize with LangChain document processor."""
        self.processor = DocumentProcessor()
    
    async def process(
        self,
        file_content: bytes,
        filename: str,
    ) -> ProcessedDocument:
        """Process a document and extract text.
        
        Args:
            file_content: Raw bytes of the document.
            filename: Original filename (determines parser).
        
        Returns:
            ProcessedDocument with text and chunks.
        
        Raises:
            ValueError: If file type is unsupported.
        """
        return await self.processor.process_upload(file_content, filename)


@dataclass
class EmbeddingTools:
    """Embedding generation and retrieval utilities.
    
    Provides methods for creating and searching vector embeddings
    using LangChain and pgvector.
    
    Attributes:
        service: LangChain EmbeddingService instance.
    
    Example:
        >>> tools = EmbeddingTools(session)
        >>> await tools.store(cv_id, chunks)
        >>> similar = await tools.search(cv_id, "Python experience", k=5)
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session.
        
        Args:
            session: AsyncSession for database operations.
        """
        self.service = EmbeddingService(session)
    
    async def store(
        self,
        cv_id: uuid.UUID,
        chunks: List[str],
    ) -> int:
        """Store embeddings for CV chunks.
        
        Args:
            cv_id: UUID of the CV.
            chunks: List of text chunks to embed.
        
        Returns:
            Number of embeddings stored.
        """
        embeddings = await self.service.store_cv_embeddings(cv_id, chunks)
        return len(embeddings)
    
    async def search(
        self,
        cv_id: uuid.UUID,
        query: str,
        k: int = 5,
    ) -> List[str]:
        """Search for similar chunks.
        
        Args:
            cv_id: UUID of the CV to search.
            query: Query text to find similar chunks for.
            k: Number of results to return.
        
        Returns:
            List of similar text chunks.
        """
        return await self.service.similarity_search(cv_id, query, k=k)


class EvaluationTools:
    """CV evaluation utilities using LangChain.
    
    Provides methods for evaluating CVs against criteria templates
    using LangChain's evaluation chain.
    
    Attributes:
        chain: LangChain EvaluationChain instance.
    
    Example:
        >>> tools = EvaluationTools()
        >>> result = await tools.evaluate(cv_text, template, criteria)
        >>> print(f"Score: {result.percentage}%")
    """
    
    def __init__(self, chain: Optional[EvaluationChain] = None) -> None:
        """Initialize with optional custom chain.
        
        Args:
            chain: Optional pre-configured EvaluationChain.
        """
        self.chain = chain or get_evaluation_chain()
    
    async def evaluate(
        self,
        cv_text: str,
        template,
        criteria_list: List,
    ) -> CVEvaluationResult:
        """Evaluate a CV against criteria.
        
        Args:
            cv_text: Full text of the CV.
            template: Evaluation template.
            criteria_list: List of criteria to evaluate against.
        
        Returns:
            CVEvaluationResult with scores and summary.
        """
        return await self.chain.evaluate_with_template(
            cv_text=cv_text,
            template=template,
            criteria_list=criteria_list,
        )


class ConversationTools:
    """Conversation utilities for RAG chat.
    
    Provides methods for generating responses to questions about
    CVs using RAG (Retrieval-Augmented Generation).
    
    Attributes:
        conversation_chain: Chain for general Q&A.
        explanation_chain: Chain for score explanations.
    
    Example:
        >>> tools = ConversationTools(session)
        >>> response = await tools.ask("What is their Python experience?", cv_text, context)
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session.
        
        Args:
            session: AsyncSession for database operations.
        """
        self.conversation_chain = ConversationChain(session)
        self.explanation_chain = ExplanationChain()
    
    async def ask(
        self,
        question: str,
        cv_text: str,
        context_chunks: List[str],
        chat_history: List[ChatMessage],
    ) -> str:
        """Generate a response to a question about a CV.
        
        Args:
            question: User's question.
            cv_text: Full text of the CV.
            context_chunks: Relevant chunks from embedding search.
            chat_history: Previous conversation messages.
        
        Returns:
            AI-generated response string.
        """
        return await self.conversation_chain.respond(
            question=question,
            cv_text=cv_text,
            context_chunks=context_chunks,
            chat_history=chat_history,
        )
    
    async def explain_score(
        self,
        criterion_name: str,
        score: int,
        max_score: int,
        reasoning: str,
        evidence: str,
        cv_text: str,
    ) -> str:
        """Generate a detailed explanation of a criterion score.
        
        Args:
            criterion_name: Name of the criterion.
            score: Score received.
            max_score: Maximum possible score.
            reasoning: Original reasoning from evaluation.
            evidence: Evidence from CV.
            cv_text: Full text of the CV.
        
        Returns:
            Detailed explanation string.
        """
        return await self.explanation_chain.explain(
            criterion_name=criterion_name,
            score=score,
            max_score=max_score,
            reasoning=reasoning,
            evidence=evidence,
            cv_text=cv_text,
        )
