"""
LangChain Configuration

Configures LLM providers (Claude, OpenAI, Gemini) and embedding models.
Supports both system API keys and user-provided BYOK keys.

LLM Providers:
    - anthropic: Claude models (claude-sonnet-4, claude-3-opus, etc.)
    - openai: GPT models (gpt-4o, gpt-4-turbo, etc.)
    - gemini: Google Gemini models (gemini-1.5-pro, gemini-1.5-flash, etc.)

Embeddings:
    - OpenAI only (text-embedding-3-small) - required for pgvector consistency
"""

from functools import lru_cache
from typing import Literal, Union

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import Field
from pydantic_settings import BaseSettings

# Import Gemini - will be available after adding langchain-google-genai
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    ChatGoogleGenerativeAI = None  # type: ignore

# Type alias for supported providers
LLMProvider = Literal["anthropic", "openai", "gemini"]


class LangChainSettings(BaseSettings):
    """LangChain configuration settings loaded from environment variables."""
    
    # API Keys
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    
    # Model Configuration
    default_llm_provider: LLMProvider = Field(
        default="anthropic",
        alias="DEFAULT_LLM_PROVIDER"
    )
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        alias="ANTHROPIC_MODEL"
    )
    openai_model: str = Field(
        default="gpt-4o",
        alias="OPENAI_MODEL"
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        alias="GEMINI_MODEL"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="EMBEDDING_MODEL"
    )
    
    # Model Parameters
    llm_temperature: float = Field(default=0.0, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=4096, alias="LLM_MAX_TOKENS")
    
    # Embedding Dimensions
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_langchain_settings() -> LangChainSettings:
    """Get cached LangChain settings instance."""
    return LangChainSettings()


def get_llm(
    provider: LLMProvider | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> Union[ChatAnthropic, ChatOpenAI, "ChatGoogleGenerativeAI"]:
    """
    Get a configured LLM instance.
    
    Args:
        provider: LLM provider to use ("anthropic", "openai", "gemini").
                  Defaults to settings.default_llm_provider.
        api_key: Override API key (for BYOK). Uses system key if not provided.
        temperature: Override temperature. Defaults to settings.llm_temperature.
        max_tokens: Override max tokens. Defaults to settings.llm_max_tokens.
    
    Returns:
        Configured LLM instance (ChatAnthropic, ChatOpenAI, or ChatGoogleGenerativeAI).
    
    Raises:
        ValueError: If no API key is available for the selected provider.
        ImportError: If Gemini is selected but langchain-google-genai is not installed.
    
    Example:
        ```python
        # Use default provider with system API key
        llm = get_llm()
        
        # Use Gemini with BYOK
        llm = get_llm(provider="gemini", api_key=user_google_key)
        
        # Override parameters
        llm = get_llm(temperature=0.7, max_tokens=2000)
        ```
    """
    settings = get_langchain_settings()
    
    provider = provider or settings.default_llm_provider
    temperature = temperature if temperature is not None else settings.llm_temperature
    max_tokens = max_tokens or settings.llm_max_tokens
    
    if provider == "anthropic":
        key = api_key or settings.anthropic_api_key
        if not key:
            raise ValueError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable or provide api_key parameter."
            )
        return ChatAnthropic(
            model=settings.anthropic_model,
            api_key=key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    elif provider == "openai":
        key = api_key or settings.openai_api_key
        if not key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or provide api_key parameter."
            )
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    elif provider == "gemini":
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Gemini support requires langchain-google-genai package. "
                "Install it with: pip install langchain-google-genai"
            )
        key = api_key or settings.google_api_key
        if not key:
            raise ValueError(
                "Google API key not configured. "
                "Set GOOGLE_API_KEY environment variable or provide api_key parameter."
            )
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=key,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Supported: anthropic, openai, gemini")


def get_embeddings(
    api_key: str | None = None,
    model: str | None = None,
    dimensions: int | None = None,
) -> OpenAIEmbeddings:
    """
    Get a configured embeddings model instance.
    
    Currently uses OpenAI embeddings (text-embedding-3-small) as they are
    cost-effective and widely supported. Can be extended to support other
    embedding providers.
    
    Args:
        api_key: Override API key (for BYOK). Uses system key if not provided.
        model: Override embedding model. Defaults to settings.embedding_model.
        dimensions: Override embedding dimensions. Defaults to settings.embedding_dimensions.
    
    Returns:
        Configured OpenAIEmbeddings instance.
    
    Raises:
        ValueError: If no OpenAI API key is available.
    
    Example:
        ```python
        # Use default settings
        embeddings = get_embeddings()
        
        # Embed a single text
        vector = await embeddings.aembed_query("Software engineer with React")
        
        # Embed multiple texts
        vectors = await embeddings.aembed_documents(["text1", "text2"])
        ```
    """
    settings = get_langchain_settings()
    
    key = api_key or settings.openai_api_key
    if not key:
        raise ValueError(
            "OpenAI API key not configured for embeddings. "
            "Set OPENAI_API_KEY environment variable or provide api_key parameter."
        )
    
    return OpenAIEmbeddings(
        model=model or settings.embedding_model,
        api_key=key,
        dimensions=dimensions or settings.embedding_dimensions,
    )
