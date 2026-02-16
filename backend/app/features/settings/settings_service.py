"""
Settings Service

Business logic for user API keys and agent configuration.
Handles validation, encryption, and provider availability checks.
"""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.settings.settings_repository import SettingsRepository
from app.features.settings.settings_schemas import (
    ApiKeyInfo,
    ApiKeyListResponse,
    SetApiKeyResponse,
    AgentConfigResponse,
    AvailableModelsResponse,
    ProviderModels,
    ModelOption,
    ValidateKeyResponse,
)


# Available models per provider
AVAILABLE_MODELS = {
    "anthropic": ProviderModels(
        provider="anthropic",
        provider_name="Anthropic (Claude)",
        models=[
            # Latest Claude 4.x models (2025-2026)
            ModelOption(
                id="claude-opus-4-6",
                name="Claude Opus 4.6",
                description="Most intelligent model for complex tasks"
            ),
            ModelOption(
                id="claude-sonnet-4-5-20250929",
                name="Claude Sonnet 4.5",
                description="Best balance of speed and intelligence"
            ),
            ModelOption(
                id="claude-haiku-4-5-20251001",
                name="Claude Haiku 4.5",
                description="Fastest with excellent intelligence"
            ),
            # Previous Claude 4.x models
            ModelOption(
                id="claude-opus-4-20250514",
                name="Claude Opus 4",
                description="Previous Opus generation"
            ),
            ModelOption(
                id="claude-sonnet-4-20250514",
                name="Claude Sonnet 4",
                description="Previous Sonnet generation"
            ),
            ModelOption(
                id="claude-haiku-4-20250514",
                name="Claude Haiku 4",
                description="Previous Haiku generation"
            ),
            # Legacy Claude 3.5 models
            ModelOption(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                description="Legacy Sonnet model"
            ),
            ModelOption(
                id="claude-3-5-haiku-20241022",
                name="Claude 3.5 Haiku",
                description="Legacy Haiku model"
            ),
        ]
    ),
    "openai": ProviderModels(
        provider="openai",
        provider_name="OpenAI (GPT)",
        models=[
            # Frontier models (GPT-5.x) - Recommended
            ModelOption(
                id="gpt-5.2",
                name="GPT-5.2",
                description="Best model for coding and agentic tasks"
            ),
            ModelOption(
                id="gpt-5.2-pro",
                name="GPT-5.2 Pro",
                description="Smarter and more precise responses"
            ),
            ModelOption(
                id="gpt-5",
                name="GPT-5",
                description="Intelligent reasoning with configurable effort"
            ),
            ModelOption(
                id="gpt-5-mini",
                name="GPT-5 Mini",
                description="Faster, cost-efficient for well-defined tasks"
            ),
            ModelOption(
                id="gpt-5-nano",
                name="GPT-5 Nano",
                description="Fastest, most cost-efficient"
            ),
            # Previous generation
            ModelOption(
                id="gpt-4.1",
                name="GPT-4.1",
                description="Smartest non-reasoning model"
            ),
            ModelOption(
                id="gpt-4.1-mini",
                name="GPT-4.1 Mini",
                description="Fast and affordable"
            ),
            ModelOption(
                id="gpt-4.1-nano",
                name="GPT-4.1 Nano",
                description="Fastest GPT-4.1 variant"
            ),
            # Reasoning models
            ModelOption(
                id="o3",
                name="o3",
                description="Advanced reasoning model"
            ),
            ModelOption(
                id="o4-mini",
                name="o4-mini",
                description="Latest reasoning, cost-effective"
            ),
        ]
    ),
    "gemini": ProviderModels(
        provider="gemini",
        provider_name="Google (Gemini)",
        models=[
            # Latest Gemini 3.x models
            ModelOption(
                id="gemini-3-pro",
                name="Gemini 3 Pro",
                description="Most intelligent, best for multimodal and agentic tasks"
            ),
            ModelOption(
                id="gemini-3-flash",
                name="Gemini 3 Flash",
                description="Most balanced, built for speed and scale"
            ),
            # Gemini 2.5 models
            ModelOption(
                id="gemini-2.5-pro",
                name="Gemini 2.5 Pro",
                description="Advanced thinking model for complex reasoning"
            ),
            ModelOption(
                id="gemini-2.5-flash",
                name="Gemini 2.5 Flash",
                description="Best price-performance, great for large scale"
            ),
            ModelOption(
                id="gemini-2.5-flash-lite",
                name="Gemini 2.5 Flash-Lite",
                description="Fastest flash, optimized for cost-efficiency"
            ),
            # Deprecated (until March 31, 2026)
            ModelOption(
                id="gemini-2.0-flash",
                name="Gemini 2.0 Flash",
                description="Deprecated - shutting down March 31, 2026"
            ),
        ]
    ),
}


class SettingsService:
    """Service for managing user settings.
    
    Handles API key management, validation, and agent configuration.
    Enforces that OpenAI API key is required for embeddings.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize service with database session.
        
        Args:
            session: Async SQLAlchemy session.
        """
        self.repository = SettingsRepository(session)
    
    # =========================================================================
    # API KEY METHODS
    # =========================================================================
    
    async def get_api_keys(self, user_id: uuid.UUID) -> ApiKeyListResponse:
        """Get all API keys for a user.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            ApiKeyListResponse with key hints and OpenAI status.
        """
        keys = await self.repository.get_api_keys(user_id)
        
        key_infos = [
            ApiKeyInfo(
                provider=key.provider,
                key_hint=f"...{key.key_hint}",
                is_valid=key.is_valid,
                is_required=(key.provider == "openai")
            )
            for key in keys
        ]
        
        # Check if OpenAI is configured
        openai_configured = any(k.provider == "openai" for k in keys)
        
        return ApiKeyListResponse(
            keys=key_infos,
            openai_configured=openai_configured
        )
    
    async def set_api_key(
        self,
        user_id: uuid.UUID,
        provider: str,
        api_key: str,
        validate: bool = True
    ) -> SetApiKeyResponse:
        """Set or update an API key.
        
        Args:
            user_id: User's UUID.
            provider: AI provider name (openai, anthropic, gemini).
            api_key: Plain text API key.
            validate: Whether to validate the key before storing.
            
        Returns:
            SetApiKeyResponse with result.
        """
        is_valid = True
        message = "API key stored successfully"
        
        if validate:
            validation = await self.validate_api_key(provider, api_key)
            is_valid = validation.is_valid
            if not is_valid:
                message = f"Key stored but validation failed: {validation.message}"
        
        key_record = await self.repository.set_api_key(
            user_id=user_id,
            provider=provider,
            api_key=api_key,
            is_valid=is_valid
        )
        
        return SetApiKeyResponse(
            provider=provider,
            key_hint=f"...{key_record.key_hint}",
            is_valid=is_valid,
            message=message
        )
    
    async def delete_api_key(self, user_id: uuid.UUID, provider: str) -> bool:
        """Delete an API key.
        
        Args:
            user_id: User's UUID.
            provider: AI provider name.
            
        Returns:
            True if deleted, False if not found.
            
        Raises:
            ValueError: If trying to delete required OpenAI key.
        """
        # Note: We allow deletion but warn in the response
        return await self.repository.delete_api_key(user_id, provider)
    
    async def validate_api_key(
        self,
        provider: str,
        api_key: str
    ) -> ValidateKeyResponse:
        """Validate an API key by making a test request.
        
        Args:
            provider: AI provider name.
            api_key: API key to validate.
            
        Returns:
            ValidateKeyResponse with validation result.
        """
        try:
            if provider == "openai":
                return await self._validate_openai_key(api_key)
            elif provider == "anthropic":
                return await self._validate_anthropic_key(api_key)
            elif provider == "gemini":
                return await self._validate_gemini_key(api_key)
            else:
                return ValidateKeyResponse(
                    provider=provider,
                    is_valid=False,
                    message=f"Unknown provider: {provider}"
                )
        except Exception as e:
            return ValidateKeyResponse(
                provider=provider,
                is_valid=False,
                message=str(e)
            )
    
    async def _validate_openai_key(self, api_key: str) -> ValidateKeyResponse:
        """Validate OpenAI API key."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            # Make a minimal API call to validate
            client.models.list()
            return ValidateKeyResponse(
                provider="openai",
                is_valid=True,
                message="OpenAI API key is valid"
            )
        except Exception as e:
            return ValidateKeyResponse(
                provider="openai",
                is_valid=False,
                message=f"Invalid OpenAI API key: {str(e)}"
            )
    
    async def _validate_anthropic_key(self, api_key: str) -> ValidateKeyResponse:
        """Validate Anthropic API key."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            # Make a minimal API call to validate
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return ValidateKeyResponse(
                provider="anthropic",
                is_valid=True,
                message="Anthropic API key is valid"
            )
        except Exception as e:
            return ValidateKeyResponse(
                provider="anthropic",
                is_valid=False,
                message=f"Invalid Anthropic API key: {str(e)}"
            )
    
    async def _validate_gemini_key(self, api_key: str) -> ValidateKeyResponse:
        """Validate Google Gemini API key."""
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            # Make a minimal API call to validate
            client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Hi",
                config={"max_output_tokens": 1}
            )
            return ValidateKeyResponse(
                provider="gemini",
                is_valid=True,
                message="Gemini API key is valid"
            )
        except Exception as e:
            return ValidateKeyResponse(
                provider="gemini",
                is_valid=False,
                message=f"Invalid Gemini API key: {str(e)}"
            )
    
    async def get_user_api_key(
        self,
        user_id: uuid.UUID,
        provider: str
    ) -> Optional[str]:
        """Get decrypted API key for a user.
        
        This is used internally by LangChain config to get BYOK keys.
        
        Args:
            user_id: User's UUID.
            provider: AI provider name.
            
        Returns:
            Decrypted API key if found, None otherwise.
        """
        return await self.repository.get_decrypted_key(user_id, provider)
    
    async def check_openai_configured(self, user_id: uuid.UUID) -> bool:
        """Check if user has OpenAI API key configured.
        
        OpenAI is required for embeddings.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            True if OpenAI key is configured.
        """
        key = await self.repository.get_api_key(user_id, "openai")
        return key is not None and key.is_valid
    
    # =========================================================================
    # AGENT CONFIG METHODS
    # =========================================================================
    
    async def get_agent_config(self, user_id: uuid.UUID) -> AgentConfigResponse:
        """Get user's agent configuration.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            AgentConfigResponse with current settings.
        """
        config = await self.repository.get_or_create_agent_config(user_id)
        
        return AgentConfigResponse(
            default_llm_provider=config.chat_provider or "anthropic",
            default_llm_model=config.chat_model,
            parser_provider=config.parser_provider,
            parser_model=config.parser_model,
            chat_provider=config.chat_provider,
            chat_model=config.chat_model,
            scorer_provider=config.scorer_provider,
            scorer_model=config.scorer_model,
            # Embeddings always OpenAI
            embeddings_provider="openai",
            embeddings_model="text-embedding-3-small"
        )
    
    async def update_agent_config(
        self,
        user_id: uuid.UUID,
        default_llm_provider: Optional[str] = None,
        default_llm_model: Optional[str] = None,
        parser_provider: Optional[str] = None,
        parser_model: Optional[str] = None,
        chat_provider: Optional[str] = None,
        chat_model: Optional[str] = None,
        scorer_provider: Optional[str] = None,
        scorer_model: Optional[str] = None,
    ) -> AgentConfigResponse:
        """Update user's agent configuration.
        
        Note: Embeddings cannot be changed (always OpenAI).
        
        Args:
            user_id: User's UUID.
            default_llm_provider: Default provider for all agents.
            default_llm_model: Default model name.
            parser_provider: Override for parser agent.
            parser_model: Override model for parser.
            chat_provider: Override for chat agent.
            chat_model: Override model for chat.
            scorer_provider: Override for scorer agent.
            scorer_model: Override model for scorer.
            
        Returns:
            Updated AgentConfigResponse.
        """
        # Use default for unset per-agent configs
        effective_parser = parser_provider or default_llm_provider
        effective_chat = chat_provider or default_llm_provider
        effective_scorer = scorer_provider or default_llm_provider
        effective_parser_model = parser_model or default_llm_model
        effective_chat_model = chat_model or default_llm_model
        effective_scorer_model = scorer_model or default_llm_model
        
        await self.repository.update_agent_config(
            user_id=user_id,
            parser_provider=effective_parser,
            parser_model=effective_parser_model,
            chat_provider=effective_chat,
            chat_model=effective_chat_model,
            scorer_provider=effective_scorer,
            scorer_model=effective_scorer_model,
        )
        
        return await self.get_agent_config(user_id)
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_available_models(self) -> AvailableModelsResponse:
        """Get all available LLM providers and models.
        
        Returns:
            AvailableModelsResponse with provider/model options.
        """
        return AvailableModelsResponse(
            providers=list(AVAILABLE_MODELS.values())
        )
