"""
LangChain Chains

This module contains LangChain chain definitions for various tasks:
- evaluation_chain: CV evaluation with structured output
- conversation_chain: RAG-powered Q&A about CVs
"""

from app.langchain.chains.evaluation_chain import (
    EvaluationChain,
    CriterionScore,
    CVEvaluationResult,
)
from app.langchain.chains.conversation_chain import (
    ConversationChain,
    ChatMessage,
)

__all__ = [
    "EvaluationChain",
    "CriterionScore",
    "CVEvaluationResult",
    "ConversationChain",
    "ChatMessage",
]
