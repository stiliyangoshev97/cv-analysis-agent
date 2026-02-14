"""
User Settings Feature Module

Manages user API keys and AI provider configuration.
Users must provide OpenAI API key for embeddings (mandatory),
and can optionally configure their preferred LLM provider.

Endpoints:
    GET  /api/settings/api-keys        - List user's API keys (hints only)
    PUT  /api/settings/api-keys/{provider} - Set/update API key
    DELETE /api/settings/api-keys/{provider} - Delete API key
    GET  /api/settings/agent-config    - Get user's LLM preferences
    PUT  /api/settings/agent-config    - Update LLM preferences
    POST /api/settings/validate-key    - Validate an API key
"""

from app.features.settings.settings_routes import router as settings_router

__all__ = ["settings_router"]
