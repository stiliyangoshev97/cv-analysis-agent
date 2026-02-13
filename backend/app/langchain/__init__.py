"""
LangChain Integration Module

This module provides LangChain-based AI capabilities for the CV Screening Agent:
- Document processing (PDF/DOCX loading, text splitting)
- Embedding generation (OpenAI embeddings → pgvector)
- CV evaluation chains (structured output with Claude)
- RAG conversation chains (context-aware chat)

Module Structure:
    - config.py: LLM and embedding model configuration
    - document_processor.py: PDF/DOCX loading and text chunking
    - embeddings.py: Embedding generation and storage
    - chains/: Chain definitions for various tasks
        - evaluation_chain.py: CV evaluation with structured output
        - conversation_chain.py: RAG-powered Q&A

Example Usage:
    ```python
    from app.langchain import (
        DocumentProcessor,
        EmbeddingService,
        EvaluationChain,
        ConversationChain,
    )
    
    # Process a CV document
    processor = DocumentProcessor()
    result = await processor.process_upload(file_content, "resume.pdf")
    
    # Store embeddings
    embedding_service = EmbeddingService(session)
    await embedding_service.store_cv_embeddings(cv.id, result.chunks)
    
    # Evaluate the CV
    eval_chain = EvaluationChain()
    evaluation = await eval_chain.evaluate(
        cv_text=result.full_text,
        template_name="AI-First Fintech",
        criteria=criteria_list,
    )
    
    # Chat about the CV
    chat_chain = ConversationChain(session)
    response = await chat_chain.ask(cv.id, "What is their experience?")
    ```
"""

# Configuration
from app.langchain.config import (
    get_llm,
    get_embeddings,
    get_langchain_settings,
    LangChainSettings,
)

# Document Processing
from app.langchain.document_processor import (
    DocumentProcessor,
    ProcessedDocument,
    load_document,
    load_document_from_bytes,
    process_documents,
    extract_full_text,
)

# Embeddings
from app.langchain.embeddings import (
    EmbeddingService,
    embed_text,
    embed_texts,
    embed_documents,
)

# Chains
from app.langchain.chains.evaluation_chain import (
    EvaluationChain,
    CriterionScore,
    CVEvaluationResult,
    get_evaluation_chain,
)
from app.langchain.chains.conversation_chain import (
    ConversationChain,
    ExplanationChain,
    ChatMessage,
)

__all__ = [
    # Config
    "get_llm",
    "get_embeddings",
    "get_langchain_settings",
    "LangChainSettings",
    # Document Processing
    "DocumentProcessor",
    "ProcessedDocument",
    "load_document",
    "load_document_from_bytes",
    "process_documents",
    "extract_full_text",
    # Embeddings
    "EmbeddingService",
    "embed_text",
    "embed_texts",
    "embed_documents",
    # Evaluation Chain
    "EvaluationChain",
    "CriterionScore",
    "CVEvaluationResult",
    "get_evaluation_chain",
    # Conversation Chain
    "ConversationChain",
    "ExplanationChain",
    "ChatMessage",
]
