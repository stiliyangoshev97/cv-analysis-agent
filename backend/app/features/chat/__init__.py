"""Chat feature module.

This module provides RAG-powered chat functionality for asking questions
about CVs. Uses vector embeddings for context retrieval and LangChain
for conversational AI responses.

Architecture (Controller-Service-Repository Pattern):
    - chat_routes.py: Route definitions (thin)
    - chat_controller.py: HTTP request/response handling
    - chat_service.py: Orchestration and RAG logic
    - chat_repository.py: Chat history database operations
    - chat_schemas.py: Pydantic validation schemas
    - chat_dependencies.py: FastAPI dependencies

Exports:
    chat_router: FastAPI router with chat endpoints.
    ChatService: Orchestration service for RAG chat.
    ChatRepository: Chat history database operations.
"""

from .chat_routes import router as chat_router
from .chat_service import ChatService
from .chat_repository import ChatRepository
from .chat_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    ExplainCriterionRequest,
    ExplainCriterionResponse,
    CompareRequest,
    CompareResponse,
    AskResponse,
)

__all__ = [
    # Router
    "chat_router",
    # Services
    "ChatService",
    # Repositories
    "ChatRepository",
    # Schemas
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ExplainCriterionRequest",
    "ExplainCriterionResponse",
    "CompareRequest",
    "CompareResponse",
    "AskResponse",
]
