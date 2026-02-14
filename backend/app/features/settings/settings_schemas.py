"""
User Settings Pydantic Schemas

Defines request/response models for API key and agent configuration endpoints.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# =============================================================================
# API KEY SCHEMAS
# =============================================================================

AIProviderType = Literal["openai", "anthropic", "gemini"]


class ApiKeyInfo(BaseModel):
    """API key information (without exposing the actual key).
    
    Attributes:
        provider: AI provider name.
        key_hint: Last 4 characters of the key for identification.
        is_valid: Whether the key has been validated.
        is_required: Whether this key is required (OpenAI for embeddings).
    """
    provider: str
    key_hint: str
    is_valid: bool
    is_required: bool = False


class ApiKeyListResponse(BaseModel):
    """Response listing all user API keys.
    
    Attributes:
        keys: List of API key info (hints only, not actual keys).
        openai_configured: Whether OpenAI API key is configured (required).
    """
    keys: list[ApiKeyInfo]
    openai_configured: bool


class SetApiKeyRequest(BaseModel):
    """Request to set/update an API key.
    
    Attributes:
        api_key: The API key to store (will be encrypted).
    """
    api_key: str = Field(..., min_length=10, description="API key to store")


class SetApiKeyResponse(BaseModel):
    """Response after setting an API key.
    
    Attributes:
        provider: AI provider name.
        key_hint: Last 4 characters of the stored key.
        is_valid: Whether the key was validated successfully.
        message: Status message.
    """
    provider: str
    key_hint: str
    is_valid: bool
    message: str


class ValidateKeyRequest(BaseModel):
    """Request to validate an API key without storing.
    
    Attributes:
        provider: AI provider to validate against.
        api_key: The API key to validate.
    """
    provider: AIProviderType
    api_key: str = Field(..., min_length=10)


class ValidateKeyResponse(BaseModel):
    """Response from API key validation.
    
    Attributes:
        provider: AI provider name.
        is_valid: Whether the key is valid.
        message: Validation result message.
    """
    provider: str
    is_valid: bool
    message: str


# =============================================================================
# AGENT CONFIG SCHEMAS
# =============================================================================

LLMProviderType = Literal["anthropic", "openai", "gemini"]


class AgentConfigResponse(BaseModel):
    """User's agent configuration preferences.
    
    Note: Embeddings are always OpenAI (not configurable by user).
    
    Attributes:
        default_llm_provider: User's preferred LLM provider.
        default_llm_model: User's preferred model for the provider.
        chat_provider: Provider for chat/RAG (overrides default).
        chat_model: Model for chat/RAG.
        scorer_provider: Provider for CV evaluation (overrides default).
        scorer_model: Model for CV evaluation.
    """
    default_llm_provider: Optional[LLMProviderType] = "anthropic"
    default_llm_model: Optional[str] = None
    
    # Per-agent overrides (optional)
    chat_provider: Optional[LLMProviderType] = None
    chat_model: Optional[str] = None
    scorer_provider: Optional[LLMProviderType] = None
    scorer_model: Optional[str] = None
    
    # Read-only (not user configurable)
    embeddings_provider: str = "openai"
    embeddings_model: str = "text-embedding-3-small"


class UpdateAgentConfigRequest(BaseModel):
    """Request to update agent configuration.
    
    Note: Users cannot change embeddings provider (always OpenAI).
    
    Attributes:
        default_llm_provider: Preferred LLM provider for all agents.
        default_llm_model: Preferred model name.
        chat_provider: Override for chat agent.
        chat_model: Override model for chat.
        scorer_provider: Override for scorer agent.
        scorer_model: Override model for scorer.
    """
    default_llm_provider: Optional[LLMProviderType] = None
    default_llm_model: Optional[str] = None
    chat_provider: Optional[LLMProviderType] = None
    chat_model: Optional[str] = None
    scorer_provider: Optional[LLMProviderType] = None
    scorer_model: Optional[str] = None


# =============================================================================
# AVAILABLE MODELS
# =============================================================================

class ModelOption(BaseModel):
    """A model option for a provider."""
    id: str
    name: str
    description: str


class ProviderModels(BaseModel):
    """Available models for a provider."""
    provider: str
    provider_name: str
    models: list[ModelOption]


class AvailableModelsResponse(BaseModel):
    """Response listing all available LLM providers and models."""
    providers: list[ProviderModels]
