"""
Settings Controller

HTTP handlers for user settings endpoints.
Handles request parsing, response formatting, and error handling.
"""

import uuid
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.settings.settings_service import SettingsService
from app.features.settings.settings_schemas import (
    SetApiKeyRequest,
    SetApiKeyResponse,
    ApiKeyListResponse,
    AgentConfigResponse,
    UpdateAgentConfigRequest,
    AvailableModelsResponse,
    ValidateKeyRequest,
    ValidateKeyResponse,
)


class SettingsController:
    """HTTP controller for user settings endpoints."""
    
    # =========================================================================
    # API KEY ENDPOINTS
    # =========================================================================
    
    @staticmethod
    async def get_api_keys(
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> ApiKeyListResponse:
        """Get all API keys for the current user.
        
        Returns key hints only, not actual keys.
        
        Args:
            session: Database session.
            user_id: Current user's ID.
            
        Returns:
            ApiKeyListResponse with key hints and status.
        """
        service = SettingsService(session)
        return await service.get_api_keys(user_id)
    
    @staticmethod
    async def set_api_key(
        session: AsyncSession,
        user_id: uuid.UUID,
        provider: Literal["openai", "anthropic", "gemini"],
        request: SetApiKeyRequest
    ) -> SetApiKeyResponse:
        """Set or update an API key for a provider.
        
        Args:
            session: Database session.
            user_id: Current user's ID.
            provider: AI provider name.
            request: Request with API key.
            
        Returns:
            SetApiKeyResponse with result.
        """
        service = SettingsService(session)
        return await service.set_api_key(
            user_id=user_id,
            provider=provider,
            api_key=request.api_key,
            validate=True
        )
    
    @staticmethod
    async def delete_api_key(
        session: AsyncSession,
        user_id: uuid.UUID,
        provider: Literal["openai", "anthropic", "gemini"]
    ) -> dict:
        """Delete an API key.
        
        Warning: Deleting OpenAI key will prevent CV uploads (embeddings).
        
        Args:
            session: Database session.
            user_id: Current user's ID.
            provider: AI provider name.
            
        Returns:
            Success message.
            
        Raises:
            HTTPException: If key not found.
        """
        service = SettingsService(session)
        deleted = await service.delete_api_key(user_id, provider)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No API key found for provider: {provider}"
            )
        
        warning = ""
        if provider == "openai":
            warning = " Warning: OpenAI key is required for CV uploads (embeddings)."
        
        return {
            "message": f"API key for {provider} deleted successfully.{warning}"
        }
    
    @staticmethod
    async def validate_api_key(
        session: AsyncSession,
        request: ValidateKeyRequest
    ) -> ValidateKeyResponse:
        """Validate an API key without storing it.
        
        Args:
            session: Database session.
            request: Validation request with provider and key.
            
        Returns:
            ValidateKeyResponse with validation result.
        """
        service = SettingsService(session)
        return await service.validate_api_key(
            provider=request.provider,
            api_key=request.api_key
        )
    
    # =========================================================================
    # AGENT CONFIG ENDPOINTS
    # =========================================================================
    
    @staticmethod
    async def get_agent_config(
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> AgentConfigResponse:
        """Get user's LLM preferences.
        
        Args:
            session: Database session.
            user_id: Current user's ID.
            
        Returns:
            AgentConfigResponse with current config.
        """
        service = SettingsService(session)
        return await service.get_agent_config(user_id)
    
    @staticmethod
    async def update_agent_config(
        session: AsyncSession,
        user_id: uuid.UUID,
        request: UpdateAgentConfigRequest
    ) -> AgentConfigResponse:
        """Update user's LLM preferences.
        
        Note: Embeddings provider cannot be changed (always OpenAI).
        
        Args:
            session: Database session.
            user_id: Current user's ID.
            request: Update request.
            
        Returns:
            Updated AgentConfigResponse.
        """
        service = SettingsService(session)
        return await service.update_agent_config(
            user_id=user_id,
            default_llm_provider=request.default_llm_provider,
            default_llm_model=request.default_llm_model,
            parser_provider=request.parser_provider,
            parser_model=request.parser_model,
            chat_provider=request.chat_provider,
            chat_model=request.chat_model,
            scorer_provider=request.scorer_provider,
            scorer_model=request.scorer_model,
        )
    
    # =========================================================================
    # UTILITY ENDPOINTS
    # =========================================================================
    
    @staticmethod
    async def get_available_models(session: AsyncSession) -> AvailableModelsResponse:
        """Get list of available LLM providers and models.
        
        Args:
            session: Database session.
            
        Returns:
            AvailableModelsResponse with all options.
        """
        service = SettingsService(session)
        return service.get_available_models()
    
    @staticmethod
    async def check_setup_status(
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> dict:
        """Check if user has completed required setup.
        
        Required: OpenAI API key for embeddings.
        Recommended: At least one LLM provider key.
        
        Args:
            session: Database session.
            user_id: Current user's ID.
            
        Returns:
            Setup status dict.
        """
        service = SettingsService(session)
        keys = await service.get_api_keys(user_id)
        
        openai_configured = keys.openai_configured
        llm_configured = any(
            k.provider in ("anthropic", "openai", "gemini") and k.is_valid
            for k in keys.keys
        )
        
        # Build missing items list
        missing = []
        if not openai_configured:
            missing.append("OpenAI API key (required for embeddings)")
        if not llm_configured:
            missing.append("At least one LLM provider key (Anthropic, OpenAI, or Gemini)")
        
        is_complete = openai_configured and llm_configured
        
        return {
            "is_complete": is_complete,
            "openai_configured": openai_configured,
            "llm_configured": llm_configured,
            "missing": missing,
            "ready_for_uploads": openai_configured,
            "message": (
                "Setup complete!" if is_complete
                else "Please configure OpenAI API key for embeddings." if not openai_configured
                else "Setup complete (using OpenAI for both embeddings and LLM)."
            )
        }
