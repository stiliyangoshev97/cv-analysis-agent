"""Unit tests for SettingsService.

Tests cover:
- API Key Management: get, set, delete, validate
- Agent Config: get, update
- Setup Status: check OpenAI configured
- Available Models: list providers

All external dependencies (repositories, API clients) are mocked.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.features.settings.settings_service import (
    SettingsService,
    AVAILABLE_MODELS,
)
from app.features.settings.settings_schemas import (
    ApiKeyInfo,
    ApiKeyListResponse,
    SetApiKeyResponse,
    AgentConfigResponse,
    ValidateKeyResponse,
)
from app.db.models.api_key import UserApiKey
from app.db.models.agent_config import UserAgentConfig


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_session():
    """Create a mock async session."""
    return AsyncMock()


@pytest.fixture
def sample_user_id():
    """Sample user UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_openai_key(sample_user_id):
    """Create sample OpenAI API key record."""
    return UserApiKey(
        id=uuid.uuid4(),
        user_id=sample_user_id,
        provider="openai",
        encrypted_key="encrypted_test_key",
        key_hint="xYz1",
        is_valid=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_anthropic_key(sample_user_id):
    """Create sample Anthropic API key record."""
    return UserApiKey(
        id=uuid.uuid4(),
        user_id=sample_user_id,
        provider="anthropic",
        encrypted_key="encrypted_anthropic_key",
        key_hint="AbCd",
        is_valid=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_agent_config(sample_user_id):
    """Create sample agent configuration."""
    return UserAgentConfig(
        id=uuid.uuid4(),
        user_id=sample_user_id,
        parser_provider="gemini",
        parser_model="gemini-2.0-flash",
        scorer_provider="anthropic",
        scorer_model="claude-sonnet-4-20250514",
        chat_provider="anthropic",
        chat_model="claude-sonnet-4-20250514",
        embeddings_provider="openai",
        embeddings_model="text-embedding-3-small",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def settings_service(mock_session):
    """Create SettingsService with mocked repository."""
    service = SettingsService(mock_session)
    service.repository = AsyncMock()
    return service


# =============================================================================
# Test: Get API Keys
# =============================================================================

class TestGetApiKeys:
    """Tests for SettingsService.get_api_keys()."""
    
    @pytest.mark.asyncio
    async def test_get_api_keys_empty(self, settings_service, sample_user_id):
        """Should return empty list when no keys configured."""
        settings_service.repository.get_api_keys.return_value = []
        
        result = await settings_service.get_api_keys(sample_user_id)
        
        assert isinstance(result, ApiKeyListResponse)
        assert result.keys == []
        assert result.openai_configured is False
    
    @pytest.mark.asyncio
    async def test_get_api_keys_with_openai(
        self, settings_service, sample_user_id, sample_openai_key
    ):
        """Should return OpenAI key and mark as configured."""
        settings_service.repository.get_api_keys.return_value = [sample_openai_key]
        
        result = await settings_service.get_api_keys(sample_user_id)
        
        assert len(result.keys) == 1
        assert result.keys[0].provider == "openai"
        assert result.keys[0].key_hint == "...xYz1"
        assert result.keys[0].is_valid is True
        assert result.keys[0].is_required is True
        assert result.openai_configured is True
    
    @pytest.mark.asyncio
    async def test_get_api_keys_multiple(
        self, settings_service, sample_user_id, sample_openai_key, sample_anthropic_key
    ):
        """Should return all configured keys."""
        settings_service.repository.get_api_keys.return_value = [
            sample_openai_key, sample_anthropic_key
        ]
        
        result = await settings_service.get_api_keys(sample_user_id)
        
        assert len(result.keys) == 2
        assert result.openai_configured is True
        # OpenAI should be marked as required
        openai_key = next(k for k in result.keys if k.provider == "openai")
        anthropic_key = next(k for k in result.keys if k.provider == "anthropic")
        assert openai_key.is_required is True
        assert anthropic_key.is_required is False


# =============================================================================
# Test: Set API Key
# =============================================================================

class TestSetApiKey:
    """Tests for SettingsService.set_api_key()."""
    
    @pytest.mark.asyncio
    async def test_set_api_key_success_no_validation(
        self, settings_service, sample_user_id, sample_openai_key
    ):
        """Should store key without validation when validate=False."""
        settings_service.repository.set_api_key.return_value = sample_openai_key
        
        result = await settings_service.set_api_key(
            user_id=sample_user_id,
            provider="openai",
            api_key="sk-test-key-12345",
            validate=False
        )
        
        assert isinstance(result, SetApiKeyResponse)
        assert result.provider == "openai"
        assert result.key_hint == "...xYz1"
        assert result.is_valid is True
        assert "successfully" in result.message
        
        settings_service.repository.set_api_key.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_api_key_with_validation_success(
        self, settings_service, sample_user_id, sample_openai_key
    ):
        """Should validate and store key when validate=True."""
        settings_service.repository.set_api_key.return_value = sample_openai_key
        
        # Mock the validation method to return success
        with patch.object(
            settings_service, 'validate_api_key',
            return_value=ValidateKeyResponse(
                provider="openai",
                is_valid=True,
                message="OpenAI API key is valid"
            )
        ):
            result = await settings_service.set_api_key(
                user_id=sample_user_id,
                provider="openai",
                api_key="sk-valid-key",
                validate=True
            )
        
        assert result.is_valid is True
    
    @pytest.mark.asyncio
    async def test_set_api_key_with_validation_failure(
        self, settings_service, sample_user_id, sample_openai_key
    ):
        """Should store key but mark invalid when validation fails."""
        # Return key with is_valid=False
        invalid_key = sample_openai_key
        invalid_key.is_valid = False
        settings_service.repository.set_api_key.return_value = invalid_key
        
        # Mock validation to fail
        with patch.object(
            settings_service, 'validate_api_key',
            return_value=ValidateKeyResponse(
                provider="openai",
                is_valid=False,
                message="Invalid API key"
            )
        ):
            result = await settings_service.set_api_key(
                user_id=sample_user_id,
                provider="openai",
                api_key="sk-invalid-key",
                validate=True
            )
        
        assert result.is_valid is False
        assert "validation failed" in result.message


# =============================================================================
# Test: Delete API Key
# =============================================================================

class TestDeleteApiKey:
    """Tests for SettingsService.delete_api_key()."""
    
    @pytest.mark.asyncio
    async def test_delete_api_key_success(self, settings_service, sample_user_id):
        """Should return True when key deleted."""
        settings_service.repository.delete_api_key.return_value = True
        
        result = await settings_service.delete_api_key(sample_user_id, "anthropic")
        
        assert result is True
        settings_service.repository.delete_api_key.assert_called_once_with(
            sample_user_id, "anthropic"
        )
    
    @pytest.mark.asyncio
    async def test_delete_api_key_not_found(self, settings_service, sample_user_id):
        """Should return False when key not found."""
        settings_service.repository.delete_api_key.return_value = False
        
        result = await settings_service.delete_api_key(sample_user_id, "gemini")
        
        assert result is False


# =============================================================================
# Test: Validate API Key
# =============================================================================

class TestValidateApiKey:
    """Tests for SettingsService.validate_api_key()."""
    
    @pytest.mark.asyncio
    async def test_validate_unknown_provider(self, settings_service):
        """Should return invalid for unknown provider."""
        result = await settings_service.validate_api_key(
            provider="unknown_provider",
            api_key="some-key"
        )
        
        assert result.is_valid is False
        assert "Unknown provider" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_openai_key_success(self, settings_service):
        """Should validate OpenAI key by calling API."""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.models.list.return_value = []
            mock_openai.return_value = mock_client
            
            result = await settings_service._validate_openai_key("sk-valid-key")
        
        assert result.provider == "openai"
        assert result.is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_openai_key_failure(self, settings_service):
        """Should return invalid when OpenAI API call fails."""
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.models.list.side_effect = Exception("Invalid API key")
            
            result = await settings_service._validate_openai_key("sk-invalid")
        
        assert result.is_valid is False
        assert "Invalid" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_anthropic_key_success(self, settings_service):
        """Should validate Anthropic key by calling API."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = MagicMock()
            mock_anthropic.return_value = mock_client
            
            result = await settings_service._validate_anthropic_key("sk-ant-valid")
        
        assert result.provider == "anthropic"
        assert result.is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_gemini_key_success(self, settings_service):
        """Should validate Gemini key by calling API."""
        with patch('google.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = MagicMock()
            mock_client_class.return_value = mock_client
            
            result = await settings_service._validate_gemini_key("AIza-valid")
        
        assert result.provider == "gemini"
        assert result.is_valid is True


# =============================================================================
# Test: Get User API Key (decrypted)
# =============================================================================

class TestGetUserApiKey:
    """Tests for SettingsService.get_user_api_key()."""
    
    @pytest.mark.asyncio
    async def test_get_user_api_key_exists(self, settings_service, sample_user_id):
        """Should return decrypted key when it exists."""
        settings_service.repository.get_decrypted_key.return_value = "sk-actual-key"
        
        result = await settings_service.get_user_api_key(sample_user_id, "openai")
        
        assert result == "sk-actual-key"
    
    @pytest.mark.asyncio
    async def test_get_user_api_key_not_found(self, settings_service, sample_user_id):
        """Should return None when key doesn't exist."""
        settings_service.repository.get_decrypted_key.return_value = None
        
        result = await settings_service.get_user_api_key(sample_user_id, "gemini")
        
        assert result is None


# =============================================================================
# Test: Check OpenAI Configured
# =============================================================================

class TestCheckOpenAIConfigured:
    """Tests for SettingsService.check_openai_configured()."""
    
    @pytest.mark.asyncio
    async def test_openai_configured_and_valid(
        self, settings_service, sample_user_id, sample_openai_key
    ):
        """Should return True when OpenAI key exists and is valid."""
        settings_service.repository.get_api_key.return_value = sample_openai_key
        
        result = await settings_service.check_openai_configured(sample_user_id)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_openai_not_configured(self, settings_service, sample_user_id):
        """Should return False when no OpenAI key."""
        settings_service.repository.get_api_key.return_value = None
        
        result = await settings_service.check_openai_configured(sample_user_id)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_openai_configured_but_invalid(
        self, settings_service, sample_user_id, sample_openai_key
    ):
        """Should return False when key exists but is invalid."""
        sample_openai_key.is_valid = False
        settings_service.repository.get_api_key.return_value = sample_openai_key
        
        result = await settings_service.check_openai_configured(sample_user_id)
        
        assert result is False


# =============================================================================
# Test: Get Agent Config
# =============================================================================

class TestGetAgentConfig:
    """Tests for SettingsService.get_agent_config()."""
    
    @pytest.mark.asyncio
    async def test_get_agent_config_existing(
        self, settings_service, sample_user_id, sample_agent_config
    ):
        """Should return existing agent config."""
        settings_service.repository.get_or_create_agent_config.return_value = sample_agent_config
        
        result = await settings_service.get_agent_config(sample_user_id)
        
        assert isinstance(result, AgentConfigResponse)
        assert result.chat_provider == "anthropic"
        assert result.scorer_provider == "anthropic"
        # Embeddings should always be OpenAI
        assert result.embeddings_provider == "openai"
        assert result.embeddings_model == "text-embedding-3-small"
    
    @pytest.mark.asyncio
    async def test_get_agent_config_creates_default(
        self, settings_service, sample_user_id
    ):
        """Should create default config if none exists."""
        default_config = UserAgentConfig(
            id=uuid.uuid4(),
            user_id=sample_user_id,
            chat_provider=None,
            scorer_provider=None,
        )
        settings_service.repository.get_or_create_agent_config.return_value = default_config
        
        result = await settings_service.get_agent_config(sample_user_id)
        
        # Default provider should be anthropic
        assert result.default_llm_provider == "anthropic"


# =============================================================================
# Test: Update Agent Config
# =============================================================================

class TestUpdateAgentConfig:
    """Tests for SettingsService.update_agent_config()."""
    
    @pytest.mark.asyncio
    async def test_update_agent_config_default_provider(
        self, settings_service, sample_user_id
    ):
        """Should update default provider for all agents."""
        updated_config = UserAgentConfig(
            id=uuid.uuid4(),
            user_id=sample_user_id,
            chat_provider="gemini",
            chat_model="gemini-1.5-pro",
            scorer_provider="gemini",
            scorer_model="gemini-1.5-pro",
        )
        settings_service.repository.update_agent_config.return_value = updated_config
        settings_service.repository.get_or_create_agent_config.return_value = updated_config
        
        result = await settings_service.update_agent_config(
            user_id=sample_user_id,
            default_llm_provider="gemini",
            default_llm_model="gemini-1.5-pro"
        )
        
        assert result.chat_provider == "gemini"
        assert result.scorer_provider == "gemini"
    
    @pytest.mark.asyncio
    async def test_update_agent_config_per_agent_override(
        self, settings_service, sample_user_id
    ):
        """Should allow different providers per agent."""
        updated_config = UserAgentConfig(
            id=uuid.uuid4(),
            user_id=sample_user_id,
            chat_provider="openai",
            chat_model="gpt-4o",
            scorer_provider="anthropic",
            scorer_model="claude-sonnet-4-20250514",
        )
        settings_service.repository.update_agent_config.return_value = updated_config
        settings_service.repository.get_or_create_agent_config.return_value = updated_config
        
        result = await settings_service.update_agent_config(
            user_id=sample_user_id,
            chat_provider="openai",
            chat_model="gpt-4o",
            scorer_provider="anthropic",
            scorer_model="claude-sonnet-4-20250514"
        )
        
        assert result.chat_provider == "openai"
        assert result.scorer_provider == "anthropic"


# =============================================================================
# Test: Get Available Models
# =============================================================================

class TestGetAvailableModels:
    """Tests for SettingsService.get_available_models()."""
    
    def test_get_available_models_returns_all_providers(self, settings_service):
        """Should return all available LLM providers."""
        result = settings_service.get_available_models()
        
        assert len(result.providers) == 3
        provider_names = [p.provider for p in result.providers]
        assert "anthropic" in provider_names
        assert "openai" in provider_names
        assert "gemini" in provider_names
    
    def test_get_available_models_has_anthropic_models(self, settings_service):
        """Should include Anthropic models."""
        result = settings_service.get_available_models()
        
        anthropic = next(p for p in result.providers if p.provider == "anthropic")
        assert anthropic.provider_name == "Anthropic (Claude)"
        assert len(anthropic.models) >= 2
        model_ids = [m.id for m in anthropic.models]
        assert "claude-sonnet-4-20250514" in model_ids
    
    def test_get_available_models_has_openai_models(self, settings_service):
        """Should include OpenAI models."""
        result = settings_service.get_available_models()
        
        openai = next(p for p in result.providers if p.provider == "openai")
        assert openai.provider_name == "OpenAI (GPT)"
        model_ids = [m.id for m in openai.models]
        assert "gpt-4.1" in model_ids
    
    def test_get_available_models_has_gemini_models(self, settings_service):
        """Should include Gemini models."""
        result = settings_service.get_available_models()
        
        gemini = next(p for p in result.providers if p.provider == "gemini")
        assert gemini.provider_name == "Google (Gemini)"
        model_ids = [m.id for m in gemini.models]
        assert "gemini-2.0-flash" in model_ids


# =============================================================================
# Test: AVAILABLE_MODELS constant
# =============================================================================

class TestAvailableModelsConstant:
    """Tests for the AVAILABLE_MODELS constant."""
    
    def test_has_required_providers(self):
        """Should have all three required providers."""
        assert "anthropic" in AVAILABLE_MODELS
        assert "openai" in AVAILABLE_MODELS
        assert "gemini" in AVAILABLE_MODELS
    
    def test_provider_has_required_fields(self):
        """Each provider should have required fields."""
        for provider_key, provider in AVAILABLE_MODELS.items():
            assert provider.provider == provider_key
            assert provider.provider_name
            assert len(provider.models) > 0
    
    def test_model_has_required_fields(self):
        """Each model should have required fields."""
        for provider in AVAILABLE_MODELS.values():
            for model in provider.models:
                assert model.id
                assert model.name
                assert model.description
