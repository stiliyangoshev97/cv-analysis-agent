"""Shared pytest fixtures for CV Screening Agent tests.

This module provides fixtures for:
    - Async database sessions (SQLite in-memory for speed)
    - Test client for FastAPI endpoints
    - Mock users, CVs, and other test data
    - Authentication helpers

Usage:
    Fixtures are automatically discovered by pytest.
    Import in test files or use directly::
    
        async def test_something(db_session, test_user):
            # db_session is an AsyncSession
            # test_user is a User instance
            pass
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.user import User
from app.db.models.cv import CV, CVEvaluation, CVEmbedding
from app.db.models.template import EvaluationTemplate, TemplateCriterion
from app.db.models.chat import ChatHistory
from app.core.security import hash_password, create_access_token
from app.config import Settings, get_settings


# =============================================================================
# Configuration Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Get test settings with safe defaults.
    
    Returns:
        Settings configured for testing.
    """
    return Settings(
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key="test-secret-key-for-testing-only",
        encryption_key="dGVzdC1lbmNyeXB0aW9uLWtleS0zMi1ieXRlcw==",  # Test key
        anthropic_api_key="test-api-key",
        smtp_host="",
        twilio_account_sid="",
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests.
    
    Yields:
        Event loop for the test session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="function")
async def db_engine(test_settings: Settings):
    """Create async database engine for testing.
    
    Uses SQLite in-memory for speed. Each test function gets a fresh database.
    
    Args:
        test_settings: Test settings fixture.
        
    Yields:
        Async SQLAlchemy engine.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing.
    
    Each test gets a fresh session that rolls back on completion.
    
    Args:
        db_engine: Database engine fixture.
        
    Yields:
        AsyncSession for database operations.
    """
    async_session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_factory() as session:
        yield session
        await session.rollback()


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user.
    
    Args:
        db_session: Database session fixture.
        
    Returns:
        User instance persisted to database.
    """
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        name="Test User",
        auth_provider="email",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_2(db_session: AsyncSession) -> User:
    """Create a second test user for multi-user tests.
    
    Args:
        db_session: Database session fixture.
        
    Returns:
        Second User instance.
    """
    user = User(
        id=uuid.uuid4(),
        email="user2@example.com",
        password_hash=hash_password("password456"),
        name="Second User",
        auth_provider="email",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Generate JWT token for test user.
    
    Args:
        test_user: User fixture.
        
    Returns:
        JWT access token string.
    """
    return create_access_token(str(test_user.id))


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Generate auth headers with JWT token.
    
    Args:
        auth_token: JWT token fixture.
        
    Returns:
        Headers dict with Authorization bearer token.
    """
    return {"Authorization": f"Bearer {auth_token}"}


# =============================================================================
# CV Fixtures
# =============================================================================

@pytest.fixture
async def test_cv(db_session: AsyncSession, test_user: User) -> CV:
    """Create a test CV.
    
    Args:
        db_session: Database session fixture.
        test_user: User fixture.
        
    Returns:
        CV instance persisted to database.
    """
    cv = CV(
        id=uuid.uuid4(),
        user_id=test_user.id,
        filename="test_resume.pdf",
        original_text="John Doe\nSoftware Engineer\n5 years experience in Python and FastAPI.",
        candidate_name="John Doe",
        status="evaluated",
    )
    db_session.add(cv)
    await db_session.commit()
    await db_session.refresh(cv)
    return cv


@pytest.fixture
async def test_cv_2(db_session: AsyncSession, test_user: User) -> CV:
    """Create a second test CV.
    
    Args:
        db_session: Database session fixture.
        test_user: User fixture.
        
    Returns:
        Second CV instance.
    """
    cv = CV(
        id=uuid.uuid4(),
        user_id=test_user.id,
        filename="another_resume.pdf",
        original_text="Jane Smith\nData Scientist\n3 years experience in ML and Python.",
        candidate_name="Jane Smith",
        status="evaluated",
    )
    db_session.add(cv)
    await db_session.commit()
    await db_session.refresh(cv)
    return cv


@pytest.fixture
async def test_evaluation(db_session: AsyncSession, test_cv: CV) -> CVEvaluation:
    """Create a test CV evaluation.
    
    Args:
        db_session: Database session fixture.
        test_cv: CV fixture.
        
    Returns:
        CVEvaluation instance.
    """
    evaluation = CVEvaluation(
        id=uuid.uuid4(),
        cv_id=test_cv.id,
        template_id=None,
        score=85,
        status="pass",
        reasoning="Strong candidate with relevant experience in Python and FastAPI.",
        criteria_results={
            "technical_skills": {"score": 90, "met": True},
            "experience": {"score": 80, "met": True},
        },
    )
    db_session.add(evaluation)
    await db_session.commit()
    await db_session.refresh(evaluation)
    return evaluation


@pytest.fixture
async def test_embedding(db_session: AsyncSession, test_cv: CV) -> CVEmbedding:
    """Create a test CV embedding.
    
    Args:
        db_session: Database session fixture.
        test_cv: CV fixture.
        
    Returns:
        CVEmbedding instance.
    
    Note:
        For SQLite testing, we don't create actual vector embeddings
        since pgvector is PostgreSQL-specific. Tests that need embeddings
        should mock the embedding repository.
    """
    embedding = CVEmbedding(
        id=uuid.uuid4(),
        cv_id=test_cv.id,
    )
    db_session.add(embedding)
    await db_session.commit()
    await db_session.refresh(embedding)
    return embedding


# =============================================================================
# Template Fixtures
# =============================================================================

@pytest.fixture
async def test_template(db_session: AsyncSession, test_user: User) -> EvaluationTemplate:
    """Create a test evaluation template.
    
    Args:
        db_session: Database session fixture.
        test_user: User fixture.
        
    Returns:
        EvaluationTemplate instance with criteria.
    """
    template = EvaluationTemplate(
        id=uuid.uuid4(),
        user_id=test_user.id,
        name="Software Engineer",
        description="Evaluation template for software engineers",
        is_system_template=False,
        passing_score=70,
        minimum_criteria_met=2,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(template)
    await db_session.flush()
    
    # Add criteria
    criteria = [
        TemplateCriterion(
            id=uuid.uuid4(),
            template_id=template.id,
            name="Technical Skills",
            description="Programming languages and frameworks",
            max_points=40,
            sort_order=1,
        ),
        TemplateCriterion(
            id=uuid.uuid4(),
            template_id=template.id,
            name="Experience",
            description="Years and relevance of experience",
            max_points=30,
            sort_order=2,
        ),
        TemplateCriterion(
            id=uuid.uuid4(),
            template_id=template.id,
            name="Education",
            description="Academic background",
            max_points=30,
            sort_order=3,
        ),
    ]
    for criterion in criteria:
        db_session.add(criterion)
    
    await db_session.commit()
    await db_session.refresh(template)
    return template


@pytest.fixture
async def system_template(db_session: AsyncSession) -> EvaluationTemplate:
    """Create a system evaluation template.
    
    Args:
        db_session: Database session fixture.
        
    Returns:
        System EvaluationTemplate instance.
    """
    template = EvaluationTemplate(
        id=uuid.uuid4(),
        user_id=None,  # System template
        name="General Hiring",
        description="Default evaluation template",
        is_system_template=True,
        passing_score=60,
        minimum_criteria_met=2,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    return template


# =============================================================================
# Chat Fixtures
# =============================================================================

@pytest.fixture
async def test_chat_history(db_session: AsyncSession, test_cv: CV, test_user: User) -> ChatHistory:
    """Create test chat history.
    
    Args:
        db_session: Database session fixture.
        test_cv: CV fixture.
        test_user: User fixture.
        
    Returns:
        ChatHistory instance.
    """
    chat = ChatHistory(
        id=uuid.uuid4(),
        cv_id=test_cv.id,
        user_id=test_user.id,
        role="user",
        content="What are the candidate's main skills?",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)
    return chat


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API client.
    
    Yields:
        Mocked Anthropic client.
    """
    with patch("anthropic.Anthropic") as mock:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text='{"score": 85, "status": "pass"}')]
        )
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings.
    
    Yields:
        Mocked embed_text function.
    """
    with patch("app.langchain.embeddings.embed_text") as mock:
        mock.return_value = [0.1] * 1536  # Standard OpenAI embedding size
        yield mock


@pytest.fixture
def mock_email_service():
    """Mock email notification service.
    
    Yields:
        Mocked email service.
    """
    with patch("app.features.notification.notification_service.NotificationService.send_email") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_whatsapp_service():
    """Mock WhatsApp notification service.
    
    Yields:
        Mocked WhatsApp service.
    """
    with patch("app.features.notification.notification_service.NotificationService.send_whatsapp") as mock:
        mock.return_value = True
        yield mock


# =============================================================================
# HTTP Client Fixtures
# =============================================================================

@pytest.fixture
async def client(db_session: AsyncSession, test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client for API testing.
    
    Overrides database session dependency to use test database.
    
    Args:
        db_session: Database session fixture.
        test_settings: Settings fixture.
        
    Yields:
        AsyncClient for making HTTP requests.
    """
    from app.main import app
    from app.db.session import get_async_session
    from app.config import get_settings as app_get_settings
    
    # Override dependencies
    async def override_get_session():
        yield db_session
    
    def override_get_settings():
        return test_settings
    
    app.dependency_overrides[get_async_session] = override_get_session
    app.dependency_overrides[app_get_settings] = override_get_settings
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    
    # Clear overrides
    app.dependency_overrides.clear()


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generate sample PDF bytes for upload tests.
    
    Returns:
        Minimal valid PDF file bytes.
    """
    # Minimal valid PDF
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
193
%%EOF"""
