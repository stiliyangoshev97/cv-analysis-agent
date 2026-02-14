"""
Settings Routes

API endpoints for user settings management.
Handles API keys and LLM provider configuration.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.features.auth.auth_dependencies import get_current_user
from app.features.auth.auth_schemas import UserResponse
from app.features.settings.settings_controller import SettingsController
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
from app.core.rate_limit import limiter, RATE_LIMIT_DEFAULT

router = APIRouter(prefix="/settings", tags=["Settings"])


# =============================================================================
# API KEY ENDPOINTS
# =============================================================================

@router.get(
    "/api-keys",
    response_model=ApiKeyListResponse,
    summary="Get API Keys",
    description="Get list of configured API keys (hints only, not actual keys)."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_api_keys(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> ApiKeyListResponse:
    """Get all API keys for the current user."""
    return await SettingsController.get_api_keys(session, current_user.id)


@router.put(
    "/api-keys/{provider}",
    response_model=SetApiKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Set API Key",
    description="Set or update an API key for a provider. The key is validated and encrypted before storage."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def set_api_key(
    request: Request,
    provider: Literal["openai", "anthropic", "gemini"],
    body: SetApiKeyRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> SetApiKeyResponse:
    """Set or update an API key."""
    return await SettingsController.set_api_key(
        session, current_user.id, provider, body
    )


@router.delete(
    "/api-keys/{provider}",
    status_code=status.HTTP_200_OK,
    summary="Delete API Key",
    description="Delete an API key. Warning: Deleting OpenAI key prevents CV uploads."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def delete_api_key(
    request: Request,
    provider: Literal["openai", "anthropic", "gemini"],
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> dict:
    """Delete an API key."""
    return await SettingsController.delete_api_key(
        session, current_user.id, provider
    )


@router.post(
    "/validate-key",
    response_model=ValidateKeyResponse,
    summary="Validate API Key",
    description="Validate an API key without storing it. Makes a test API call."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def validate_api_key(
    request: Request,
    body: ValidateKeyRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> ValidateKeyResponse:
    """Validate an API key without storing."""
    return await SettingsController.validate_api_key(session, body)


# =============================================================================
# AGENT CONFIG ENDPOINTS
# =============================================================================

@router.get(
    "/agent-config",
    response_model=AgentConfigResponse,
    summary="Get Agent Config",
    description="Get user's LLM provider preferences for evaluation and chat."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_agent_config(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> AgentConfigResponse:
    """Get user's agent configuration."""
    return await SettingsController.get_agent_config(session, current_user.id)


@router.put(
    "/agent-config",
    response_model=AgentConfigResponse,
    summary="Update Agent Config",
    description="Update LLM provider preferences. Embeddings always use OpenAI."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def update_agent_config(
    request: Request,
    body: UpdateAgentConfigRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> AgentConfigResponse:
    """Update user's agent configuration."""
    return await SettingsController.update_agent_config(
        session, current_user.id, body
    )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get(
    "/available-models",
    response_model=AvailableModelsResponse,
    summary="Get Available Models",
    description="Get list of all available LLM providers and their models."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_available_models(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> AvailableModelsResponse:
    """Get available LLM providers and models."""
    return await SettingsController.get_available_models(session)


@router.get(
    "/setup-status",
    summary="Get Setup Status",
    description="Check if user has completed required setup (OpenAI key for embeddings)."
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_setup_status(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserResponse = Depends(get_current_user)
) -> dict:
    """Check setup completion status."""
    return await SettingsController.check_setup_status(session, current_user.id)
