"""Unit tests for ChatService.

This module tests the ChatService class which orchestrates RAG-powered
conversations about CVs. All external dependencies (repositories, 
LangChain components) are mocked.

Test Categories:
    - _verify_cv_ownership: CV access verification
    - ask: RAG Q&A pipeline
    - get_history: Chat history retrieval
    - clear_history: Chat history clearing
    - explain_criterion: Criterion explanation
    - compare_cvs: Multi-CV comparison
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.features.chat.chat_service import ChatService, ChatResult
from app.db.models.cv import CV, CVStatus, CVEvaluation
from app.db.models.chat import ChatHistory, ChatRole


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_cv_repo():
    """Create a mock CVRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_evaluation_repo():
    """Create a mock EvaluationRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_embedding_repo():
    """Create a mock EmbeddingRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_chat_repo():
    """Create a mock ChatRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_conversation_chain():
    """Create a mock ConversationChain."""
    chain = AsyncMock()
    return chain


@pytest.fixture
def mock_explanation_chain():
    """Create a mock ExplanationChain."""
    chain = AsyncMock()
    return chain


@pytest.fixture
def sample_user_id():
    """Generate a sample user UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_cv_id():
    """Generate a sample CV UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_cv(sample_cv_id, sample_user_id):
    """Create a sample CV entity."""
    cv = MagicMock(spec=CV)
    cv.id = sample_cv_id
    cv.user_id = sample_user_id
    cv.filename = "john_doe_cv.pdf"
    cv.candidate_name = "John Doe"
    cv.original_text = "John Doe\nSoftware Engineer\n5 years Python experience..."
    cv.status = CVStatus.EVALUATED.value
    return cv


@pytest.fixture
def sample_evaluation(sample_cv_id):
    """Create a sample evaluation entity."""
    evaluation = MagicMock(spec=CVEvaluation)
    evaluation.id = uuid.uuid4()
    evaluation.cv_id = sample_cv_id
    evaluation.total_score = 75
    evaluation.passed = True
    evaluation.recommendation = "Strong candidate"
    evaluation.criteria_results = [
        {"name": "Technical Skills", "score": 25, "max_score": 30, "reasoning": "Good Python skills"},
        {"name": "Experience", "score": 20, "max_score": 25, "reasoning": "5 years experience"},
        {"name": "Education", "score": 20, "max_score": 25, "reasoning": "CS degree"},
    ]
    return evaluation


@pytest.fixture
def sample_chat_message(sample_user_id, sample_cv_id):
    """Create a sample chat message."""
    message = MagicMock(spec=ChatHistory)
    message.id = uuid.uuid4()
    message.user_id = sample_user_id
    message.cv_id = sample_cv_id
    message.role = ChatRole.ASSISTANT.value
    message.message = "John Doe has 5 years of Python experience."
    message.created_at = datetime.now(timezone.utc)
    return message


@pytest.fixture
def sample_chat_history(sample_user_id, sample_cv_id):
    """Create sample chat history messages."""
    messages = []
    for i, (role, content) in enumerate([
        (ChatRole.USER.value, "What is their experience?"),
        (ChatRole.ASSISTANT.value, "They have 5 years of Python experience."),
        (ChatRole.USER.value, "What about education?"),
        (ChatRole.ASSISTANT.value, "They have a CS degree from MIT."),
    ]):
        msg = MagicMock(spec=ChatHistory)
        msg.id = uuid.uuid4()
        msg.user_id = sample_user_id
        msg.cv_id = sample_cv_id
        msg.role = role
        msg.message = content
        msg.created_at = datetime.now(timezone.utc)
        messages.append(msg)
    return messages


@pytest.fixture
def chat_service(
    mock_session,
    mock_cv_repo,
    mock_evaluation_repo,
    mock_embedding_repo,
    mock_chat_repo,
    mock_conversation_chain,
    mock_explanation_chain,
):
    """Create a ChatService with all dependencies mocked."""
    with patch.object(ChatService, '__init__', lambda self, session: None):
        service = ChatService.__new__(ChatService)
        service.session = mock_session
        service.cv_repo = mock_cv_repo
        service.evaluation_repo = mock_evaluation_repo
        service.embedding_repo = mock_embedding_repo
        service.chat_repo = mock_chat_repo
        service.conversation_chain = mock_conversation_chain
        service.explanation_chain = mock_explanation_chain
        return service


# =============================================================================
# Test: _verify_cv_ownership
# =============================================================================

class TestVerifyCVOwnership:
    """Tests for the _verify_cv_ownership method."""
    
    @pytest.mark.asyncio
    async def test_verify_success(self, chat_service, sample_cv, sample_user_id, sample_cv_id):
        """Should return CV when owned by user."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        result = await chat_service._verify_cv_ownership(sample_cv_id, sample_user_id)
        
        assert result == sample_cv
    
    @pytest.mark.asyncio
    async def test_verify_cv_not_found(self, chat_service, sample_user_id, sample_cv_id):
        """Should raise ValueError when CV not found."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="CV not found"):
            await chat_service._verify_cv_ownership(sample_cv_id, sample_user_id)
    
    @pytest.mark.asyncio
    async def test_verify_wrong_user(self, chat_service, sample_cv, sample_cv_id):
        """Should raise ValueError when CV owned by different user."""
        other_user_id = uuid.uuid4()
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        with pytest.raises(ValueError, match="don't have access"):
            await chat_service._verify_cv_ownership(sample_cv_id, other_user_id)


# =============================================================================
# Test: ask
# =============================================================================

class TestAsk:
    """Tests for the ask method."""
    
    @pytest.mark.asyncio
    async def test_ask_success(
        self,
        chat_service,
        sample_cv,
        sample_chat_message,
        sample_user_id,
        sample_cv_id,
    ):
        """Should ask question and return response."""
        # Setup mocks
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.chat_repo.add_user_message = AsyncMock()
        chat_service.chat_repo.get_recent_messages = AsyncMock(return_value=[])
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=None)
        
        mock_response = MagicMock()
        mock_response.content = "John Doe has 5 years of Python experience."
        chat_service.conversation_chain.ask = AsyncMock(return_value=mock_response)
        chat_service.chat_repo.add_assistant_message = AsyncMock(return_value=sample_chat_message)
        
        # Mock _get_relevant_chunks
        with patch.object(chat_service, '_get_relevant_chunks', new_callable=AsyncMock) as mock_chunks:
            mock_chunks.return_value = ["Chunk 1...", "Chunk 2..."]
            
            result = await chat_service.ask(sample_cv_id, sample_user_id, "What is their experience?")
        
        assert isinstance(result, ChatResult)
        assert result.message == sample_chat_message
        assert result.sources == ["Chunk 1...", "Chunk 2..."]
        assert result.sources_count == 2
    
    @pytest.mark.asyncio
    async def test_ask_saves_user_question(
        self,
        chat_service,
        sample_cv,
        sample_chat_message,
        sample_user_id,
        sample_cv_id,
    ):
        """Should save user's question to chat history."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.chat_repo.add_user_message = AsyncMock()
        chat_service.chat_repo.get_recent_messages = AsyncMock(return_value=[])
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=None)
        
        mock_response = MagicMock()
        mock_response.content = "Answer"
        chat_service.conversation_chain.ask = AsyncMock(return_value=mock_response)
        chat_service.chat_repo.add_assistant_message = AsyncMock(return_value=sample_chat_message)
        
        with patch.object(chat_service, '_get_relevant_chunks', new_callable=AsyncMock) as mock_chunks:
            mock_chunks.return_value = []
            
            await chat_service.ask(sample_cv_id, sample_user_id, "What is their experience?")
        
        chat_service.chat_repo.add_user_message.assert_called_once_with(
            sample_user_id, sample_cv_id, "What is their experience?"
        )
    
    @pytest.mark.asyncio
    async def test_ask_cv_not_found(self, chat_service, sample_user_id, sample_cv_id):
        """Should raise ValueError when CV not found."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="CV not found"):
            await chat_service.ask(sample_cv_id, sample_user_id, "Question?")
    
    @pytest.mark.asyncio
    async def test_ask_wrong_user(self, chat_service, sample_cv, sample_cv_id):
        """Should raise ValueError when CV owned by different user."""
        other_user_id = uuid.uuid4()
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        with pytest.raises(ValueError, match="don't have access"):
            await chat_service.ask(sample_cv_id, other_user_id, "Question?")


# =============================================================================
# Test: get_history
# =============================================================================

class TestGetHistory:
    """Tests for the get_history method."""
    
    @pytest.mark.asyncio
    async def test_get_history_success(
        self,
        chat_service,
        sample_cv,
        sample_chat_history,
        sample_user_id,
        sample_cv_id,
    ):
        """Should return chat history."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.chat_repo.get_conversation = AsyncMock(return_value=sample_chat_history)
        
        result = await chat_service.get_history(sample_cv_id, sample_user_id)
        
        assert result == sample_chat_history
        assert len(result) == 4
    
    @pytest.mark.asyncio
    async def test_get_history_with_limit(
        self,
        chat_service,
        sample_cv,
        sample_user_id,
        sample_cv_id,
    ):
        """Should pass limit to repository."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.chat_repo.get_conversation = AsyncMock(return_value=[])
        
        await chat_service.get_history(sample_cv_id, sample_user_id, limit=5)
        
        chat_service.chat_repo.get_conversation.assert_called_once_with(
            sample_user_id, sample_cv_id, 5
        )
    
    @pytest.mark.asyncio
    async def test_get_history_cv_not_found(self, chat_service, sample_user_id, sample_cv_id):
        """Should raise ValueError when CV not found."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="CV not found"):
            await chat_service.get_history(sample_cv_id, sample_user_id)
    
    @pytest.mark.asyncio
    async def test_get_history_empty(
        self,
        chat_service,
        sample_cv,
        sample_user_id,
        sample_cv_id,
    ):
        """Should return empty list when no history exists."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.chat_repo.get_conversation = AsyncMock(return_value=[])
        
        result = await chat_service.get_history(sample_cv_id, sample_user_id)
        
        assert result == []


# =============================================================================
# Test: clear_history
# =============================================================================

class TestClearHistory:
    """Tests for the clear_history method."""
    
    @pytest.mark.asyncio
    async def test_clear_history_success(
        self,
        chat_service,
        sample_cv,
        sample_user_id,
        sample_cv_id,
    ):
        """Should clear history and return count."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.chat_repo.clear_conversation = AsyncMock(return_value=4)
        
        result = await chat_service.clear_history(sample_cv_id, sample_user_id)
        
        assert result == 4
        chat_service.chat_repo.clear_conversation.assert_called_once_with(
            sample_user_id, sample_cv_id
        )
    
    @pytest.mark.asyncio
    async def test_clear_history_empty(
        self,
        chat_service,
        sample_cv,
        sample_user_id,
        sample_cv_id,
    ):
        """Should return 0 when no history to clear."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.chat_repo.clear_conversation = AsyncMock(return_value=0)
        
        result = await chat_service.clear_history(sample_cv_id, sample_user_id)
        
        assert result == 0
    
    @pytest.mark.asyncio
    async def test_clear_history_cv_not_found(self, chat_service, sample_user_id, sample_cv_id):
        """Should raise ValueError when CV not found."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="CV not found"):
            await chat_service.clear_history(sample_cv_id, sample_user_id)
    
    @pytest.mark.asyncio
    async def test_clear_history_wrong_user(self, chat_service, sample_cv, sample_cv_id):
        """Should raise ValueError when CV owned by different user."""
        other_user_id = uuid.uuid4()
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        with pytest.raises(ValueError, match="don't have access"):
            await chat_service.clear_history(sample_cv_id, other_user_id)


# =============================================================================
# Test: explain_criterion
# =============================================================================

class TestExplainCriterion:
    """Tests for the explain_criterion method."""
    
    @pytest.mark.asyncio
    async def test_explain_criterion_success(
        self,
        chat_service,
        sample_cv,
        sample_evaluation,
        sample_user_id,
        sample_cv_id,
    ):
        """Should explain criterion and return result."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=sample_evaluation)
        chat_service.explanation_chain.explain = AsyncMock(
            return_value="Technical Skills score is 25/30 because of strong Python skills."
        )
        
        with patch.object(chat_service, '_get_relevant_chunks', new_callable=AsyncMock) as mock_chunks:
            mock_chunks.return_value = ["Evidence chunk..."]
            
            result = await chat_service.explain_criterion(
                sample_cv_id, sample_user_id, "Technical Skills"
            )
        
        assert result["criterion"] == "Technical Skills"
        assert result["score"] == 25
        assert result["max_score"] == 30
        assert "explanation" in result
        assert result["evidence"] == ["Evidence chunk..."]
    
    @pytest.mark.asyncio
    async def test_explain_criterion_case_insensitive(
        self,
        chat_service,
        sample_cv,
        sample_evaluation,
        sample_user_id,
        sample_cv_id,
    ):
        """Should find criterion regardless of case."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=sample_evaluation)
        chat_service.explanation_chain.explain = AsyncMock(return_value="Explanation")
        
        with patch.object(chat_service, '_get_relevant_chunks', new_callable=AsyncMock) as mock_chunks:
            mock_chunks.return_value = []
            
            # Use lowercase name
            result = await chat_service.explain_criterion(
                sample_cv_id, sample_user_id, "technical skills"
            )
        
        assert result["criterion"] == "technical skills"
    
    @pytest.mark.asyncio
    async def test_explain_criterion_cv_not_found(self, chat_service, sample_user_id, sample_cv_id):
        """Should raise ValueError when CV not found."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="CV not found"):
            await chat_service.explain_criterion(
                sample_cv_id, sample_user_id, "Technical Skills"
            )
    
    @pytest.mark.asyncio
    async def test_explain_criterion_no_evaluation(
        self,
        chat_service,
        sample_cv,
        sample_user_id,
        sample_cv_id,
    ):
        """Should raise ValueError when no evaluation exists."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="No evaluation found"):
            await chat_service.explain_criterion(
                sample_cv_id, sample_user_id, "Technical Skills"
            )
    
    @pytest.mark.asyncio
    async def test_explain_criterion_not_found(
        self,
        chat_service,
        sample_cv,
        sample_evaluation,
        sample_user_id,
        sample_cv_id,
    ):
        """Should raise ValueError when criterion doesn't exist."""
        chat_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=sample_evaluation)
        
        with pytest.raises(ValueError, match="Criterion 'Nonexistent' not found"):
            await chat_service.explain_criterion(
                sample_cv_id, sample_user_id, "Nonexistent"
            )


# =============================================================================
# Test: compare_cvs
# =============================================================================

class TestCompareCVs:
    """Tests for the compare_cvs method."""
    
    @pytest.mark.asyncio
    async def test_compare_cvs_success(
        self,
        chat_service,
        sample_cv,
        sample_evaluation,
        sample_user_id,
    ):
        """Should compare CVs and return comparison."""
        cv_id_1 = uuid.uuid4()
        cv_id_2 = uuid.uuid4()
        
        cv1 = MagicMock(spec=CV)
        cv1.id = cv_id_1
        cv1.user_id = sample_user_id
        cv1.candidate_name = "John Doe"
        cv1.filename = "john.pdf"
        
        cv2 = MagicMock(spec=CV)
        cv2.id = cv_id_2
        cv2.user_id = sample_user_id
        cv2.candidate_name = "Jane Smith"
        cv2.filename = "jane.pdf"
        
        # Setup mocks
        chat_service.cv_repo.get_by_id = AsyncMock(side_effect=[cv1, cv2])
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=sample_evaluation)
        
        with patch.object(chat_service, '_get_relevant_chunks', new_callable=AsyncMock) as mock_chunks:
            mock_chunks.return_value = ["Chunk..."]
            
            with patch('app.langchain.config.get_llm') as mock_get_llm:
                mock_llm = AsyncMock()
                mock_response = MagicMock()
                mock_response.content = "John is stronger in Python, Jane in React."
                mock_llm.ainvoke = AsyncMock(return_value=mock_response)
                mock_get_llm.return_value = mock_llm
                
                result = await chat_service.compare_cvs(
                    [cv_id_1, cv_id_2], sample_user_id
                )
        
        assert result["cv_ids"] == [cv_id_1, cv_id_2]
        assert "comparison" in result
        assert result["comparison"] == "John is stronger in Python, Jane in React."
    
    @pytest.mark.asyncio
    async def test_compare_cvs_too_few(self, chat_service, sample_user_id):
        """Should raise ValueError for fewer than 2 CVs."""
        cv_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="Must compare between 2 and 5 CVs"):
            await chat_service.compare_cvs([cv_id], sample_user_id)
    
    @pytest.mark.asyncio
    async def test_compare_cvs_too_many(self, chat_service, sample_user_id):
        """Should raise ValueError for more than 5 CVs."""
        cv_ids = [uuid.uuid4() for _ in range(6)]
        
        with pytest.raises(ValueError, match="Must compare between 2 and 5 CVs"):
            await chat_service.compare_cvs(cv_ids, sample_user_id)
    
    @pytest.mark.asyncio
    async def test_compare_cvs_one_not_found(self, chat_service, sample_cv, sample_user_id):
        """Should raise ValueError if any CV not found."""
        cv_id_1 = sample_cv.id
        cv_id_2 = uuid.uuid4()
        
        # First CV found, second not found
        chat_service.cv_repo.get_by_id = AsyncMock(side_effect=[sample_cv, None])
        
        with pytest.raises(ValueError, match="CV not found"):
            await chat_service.compare_cvs([cv_id_1, cv_id_2], sample_user_id)
    
    @pytest.mark.asyncio
    async def test_compare_cvs_one_wrong_user(self, chat_service, sample_cv, sample_user_id):
        """Should raise ValueError if any CV owned by different user."""
        cv_id_1 = sample_cv.id
        cv_id_2 = uuid.uuid4()
        
        # Second CV owned by different user
        cv2 = MagicMock(spec=CV)
        cv2.id = cv_id_2
        cv2.user_id = uuid.uuid4()  # Different user
        
        chat_service.cv_repo.get_by_id = AsyncMock(side_effect=[sample_cv, cv2])
        
        with pytest.raises(ValueError, match="don't have access"):
            await chat_service.compare_cvs([cv_id_1, cv_id_2], sample_user_id)
    
    @pytest.mark.asyncio
    async def test_compare_cvs_with_custom_question(
        self,
        chat_service,
        sample_user_id,
    ):
        """Should use custom question for comparison."""
        cv_id_1 = uuid.uuid4()
        cv_id_2 = uuid.uuid4()
        
        cv1 = MagicMock(spec=CV)
        cv1.id = cv_id_1
        cv1.user_id = sample_user_id
        cv1.candidate_name = "John"
        cv1.filename = "john.pdf"
        
        cv2 = MagicMock(spec=CV)
        cv2.id = cv_id_2
        cv2.user_id = sample_user_id
        cv2.candidate_name = "Jane"
        cv2.filename = "jane.pdf"
        
        chat_service.cv_repo.get_by_id = AsyncMock(side_effect=[cv1, cv2])
        chat_service.evaluation_repo.get_latest_by_cv = AsyncMock(return_value=None)
        
        with patch.object(chat_service, '_get_relevant_chunks', new_callable=AsyncMock) as mock_chunks:
            mock_chunks.return_value = []
            
            with patch('app.langchain.config.get_llm') as mock_get_llm:
                mock_llm = AsyncMock()
                mock_response = MagicMock()
                mock_response.content = "Both have Python skills."
                mock_llm.ainvoke = AsyncMock(return_value=mock_response)
                mock_get_llm.return_value = mock_llm
                
                result = await chat_service.compare_cvs(
                    [cv_id_1, cv_id_2],
                    sample_user_id,
                    question="Who has better Python skills?"
                )
        
        assert "comparison" in result


# =============================================================================
# Test: _get_conversation_history
# =============================================================================

class TestGetConversationHistory:
    """Tests for the _get_conversation_history helper method."""
    
    @pytest.mark.asyncio
    async def test_converts_to_chat_messages(
        self,
        chat_service,
        sample_chat_history,
        sample_user_id,
        sample_cv_id,
    ):
        """Should convert ChatHistory to ChatMessage format."""
        chat_service.chat_repo.get_recent_messages = AsyncMock(return_value=sample_chat_history)
        
        result = await chat_service._get_conversation_history(sample_user_id, sample_cv_id)
        
        assert len(result) == 4
        assert result[0].role == "user"
        assert result[0].content == "What is their experience?"
        assert result[1].role == "assistant"
    
    @pytest.mark.asyncio
    async def test_respects_limit(
        self,
        chat_service,
        sample_user_id,
        sample_cv_id,
    ):
        """Should pass limit to repository."""
        chat_service.chat_repo.get_recent_messages = AsyncMock(return_value=[])
        
        await chat_service._get_conversation_history(sample_user_id, sample_cv_id, limit=5)
        
        chat_service.chat_repo.get_recent_messages.assert_called_once_with(
            sample_user_id, sample_cv_id, 5
        )
