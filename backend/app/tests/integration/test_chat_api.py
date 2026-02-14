"""Integration tests for Chat API endpoints.

Tests cover:
- POST   /api/chat/{cv_id}                  - Ask question about CV
- GET    /api/chat/{cv_id}                  - Get chat history
- DELETE /api/chat/{cv_id}                  - Clear chat history
- POST   /api/chat/{cv_id}/explain/{criterion} - Explain criterion score
- POST   /api/chat/compare                  - Compare multiple CVs

All tests use mocked LLM responses to avoid real API calls.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.db.models.cv import CV, CVEvaluation
from app.db.models.chat import ChatHistory
from app.db.models.user import User


# =============================================================================
# Test: POST /api/chat/{cv_id} - Ask Question
# =============================================================================

class TestAskQuestion:
    """Tests for the ask question endpoint."""
    
    @pytest.mark.asyncio
    async def test_ask_question_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_cv: CV,
        test_evaluation: CVEvaluation,
    ):
        """Should ask question and return response."""
        # Mock the embedding service search (pgvector not available in SQLite)
        with patch("app.langchain.embeddings.EmbeddingService.search_similar") as mock_search:
            mock_search.return_value = []  # No similar chunks
            
            # Mock the LLM for response generation
            with patch("app.langchain.config.get_llm") as mock_get_llm:
                mock_llm = MagicMock()
                mock_response = MagicMock()
                mock_response.content = "John Doe has 5 years of Python experience with FastAPI."
                mock_llm.invoke = MagicMock(return_value=mock_response)
                mock_get_llm.return_value = mock_llm
                
                response = await client.post(
                    f"/api/chat/{test_cv.id}",
                    json={"message": "What is their Python experience?"},
                    headers=auth_headers,
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"]["role"] == "assistant"
        assert "sources_used" in data
    
    @pytest.mark.asyncio
    async def test_ask_question_cv_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Should return 404 for non-existent CV."""
        fake_cv_id = uuid.uuid4()
        
        response = await client.post(
            f"/api/chat/{fake_cv_id}",
            json={"message": "What are their skills?"},
            headers=auth_headers,
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_ask_question_unauthorized(
        self,
        client: AsyncClient,
        test_cv: CV,
    ):
        """Should return 401 without auth token."""
        response = await client.post(
            f"/api/chat/{test_cv.id}",
            json={"message": "What are their skills?"},
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_ask_question_other_user_cv(
        self,
        client: AsyncClient,
        db_session,
        test_user_2: User,
        test_cv: CV,
    ):
        """Should return 403/404 when accessing another user's CV."""
        from app.core.security import create_access_token
        
        other_token = create_access_token(str(test_user_2.id))
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        response = await client.post(
            f"/api/chat/{test_cv.id}",
            json={"message": "What are their skills?"},
            headers=other_headers,
        )
        
        # Either 403 (forbidden) or 404 (not found for security) is acceptable
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_ask_question_empty_message(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_cv: CV,
    ):
        """Should return 422 for empty message."""
        response = await client.post(
            f"/api/chat/{test_cv.id}",
            json={"message": ""},
            headers=auth_headers,
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_ask_question_message_too_long(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_cv: CV,
    ):
        """Should return 422 for message exceeding max length."""
        long_message = "x" * 2001  # Max is 2000
        
        response = await client.post(
            f"/api/chat/{test_cv.id}",
            json={"message": long_message},
            headers=auth_headers,
        )
        
        assert response.status_code == 422


# =============================================================================
# Test: GET /api/chat/{cv_id} - Get History
# =============================================================================

class TestGetHistory:
    """Tests for the get history endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_history_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_cv: CV,
    ):
        """Should return empty history for CV with no messages."""
        response = await client.get(
            f"/api/chat/{test_cv.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cv_id"] == str(test_cv.id)
        assert data["messages"] == []
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_history_with_messages(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
        test_user: User,
    ):
        """Should return history with existing messages."""
        # Create some chat messages
        messages = [
            ChatHistory(
                id=uuid.uuid4(),
                cv_id=test_cv.id,
                user_id=test_user.id,
                role="user",
                message="What is their experience?",
                created_at=datetime.now(timezone.utc),
            ),
            ChatHistory(
                id=uuid.uuid4(),
                cv_id=test_cv.id,
                user_id=test_user.id,
                role="assistant",
                message="They have 5 years of Python experience.",
                created_at=datetime.now(timezone.utc),
            ),
        ]
        for msg in messages:
            db_session.add(msg)
        await db_session.commit()
        
        response = await client.get(
            f"/api/chat/{test_cv.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cv_id"] == str(test_cv.id)
        assert len(data["messages"]) == 2
        assert data["total"] == 2
        
        # Check message structure
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][0]["content"] == "What is their experience?"
        assert data["messages"][1]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_get_history_with_limit(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
        test_user: User,
    ):
        """Should respect limit parameter."""
        # Create 5 messages
        for i in range(5):
            msg = ChatHistory(
                id=uuid.uuid4(),
                cv_id=test_cv.id,
                user_id=test_user.id,
                role="user" if i % 2 == 0 else "assistant",
                message=f"Message {i}",
                created_at=datetime.now(timezone.utc),
            )
            db_session.add(msg)
        await db_session.commit()
        
        response = await client.get(
            f"/api/chat/{test_cv.id}?limit=3",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) <= 3
    
    @pytest.mark.asyncio
    async def test_get_history_cv_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Should return 404 for non-existent CV."""
        fake_cv_id = uuid.uuid4()
        
        response = await client.get(
            f"/api/chat/{fake_cv_id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_history_unauthorized(
        self,
        client: AsyncClient,
        test_cv: CV,
    ):
        """Should return 401 without auth token."""
        response = await client.get(f"/api/chat/{test_cv.id}")
        
        assert response.status_code == 401


# =============================================================================
# Test: DELETE /api/chat/{cv_id} - Clear History
# =============================================================================

class TestClearHistory:
    """Tests for the clear history endpoint."""
    
    @pytest.mark.asyncio
    async def test_clear_history_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
        test_user: User,
    ):
        """Should clear all messages for CV."""
        # Create some messages
        for i in range(3):
            msg = ChatHistory(
                id=uuid.uuid4(),
                cv_id=test_cv.id,
                user_id=test_user.id,
                role="user",
                message=f"Message {i}",
                created_at=datetime.now(timezone.utc),
            )
            db_session.add(msg)
        await db_session.commit()
        
        response = await client.delete(
            f"/api/chat/{test_cv.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] >= 0
        
        # Verify history is empty
        history_response = await client.get(
            f"/api/chat/{test_cv.id}",
            headers=auth_headers,
        )
        assert history_response.json()["total"] == 0
    
    @pytest.mark.asyncio
    async def test_clear_history_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_cv: CV,
    ):
        """Should succeed even with no messages."""
        response = await client.delete(
            f"/api/chat/{test_cv.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 0
    
    @pytest.mark.asyncio
    async def test_clear_history_cv_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Should return 404 for non-existent CV."""
        fake_cv_id = uuid.uuid4()
        
        response = await client.delete(
            f"/api/chat/{fake_cv_id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_clear_history_unauthorized(
        self,
        client: AsyncClient,
        test_cv: CV,
    ):
        """Should return 401 without auth token."""
        response = await client.delete(f"/api/chat/{test_cv.id}")
        
        assert response.status_code == 401


# =============================================================================
# Test: POST /api/chat/{cv_id}/explain/{criterion} - Explain Criterion
# =============================================================================

class TestExplainCriterion:
    """Tests for the explain criterion endpoint."""
    
    @pytest.mark.asyncio
    async def test_explain_criterion_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
        test_user: User,
    ):
        """Should explain criterion score."""
        # Create evaluation with criteria
        evaluation = CVEvaluation(
            id=uuid.uuid4(),
            cv_id=test_cv.id,
            template_id=None,
            score=85,
            status="pass",
            reasoning="Strong candidate",
            criteria_results={
                "Technical Skills": {
                    "score": 22,
                    "max_score": 25,
                    "met": True,
                    "feedback": "Strong Python skills",
                },
            },
        )
        db_session.add(evaluation)
        await db_session.commit()
        
        # Mock embedding search (pgvector not available in SQLite)
        with patch("app.langchain.embeddings.EmbeddingService.search_similar") as mock_search:
            mock_search.return_value = []
            
            with patch("app.langchain.config.get_llm") as mock_get_llm:
                mock_llm = MagicMock()
                mock_response = MagicMock()
                mock_response.content = "The candidate scored 22/25 because they have strong Python skills."
                mock_llm.invoke = MagicMock(return_value=mock_response)
                mock_get_llm.return_value = mock_llm
                
                response = await client.post(
                    f"/api/chat/{test_cv.id}/explain/Technical Skills",
                    headers=auth_headers,
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["criterion"] == "Technical Skills"
        assert data["score"] == 22
        assert data["max_score"] == 25
        assert "explanation" in data
    
    @pytest.mark.asyncio
    async def test_explain_criterion_case_insensitive(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
    ):
        """Should match criterion name case-insensitively."""
        evaluation = CVEvaluation(
            id=uuid.uuid4(),
            cv_id=test_cv.id,
            template_id=None,
            score=75,
            status="pass",
            reasoning="Good candidate",
            criteria_results={
                "Education": {
                    "score": 12,
                    "max_score": 15,
                    "met": True,
                    "feedback": "Bachelor's degree",
                },
            },
        )
        db_session.add(evaluation)
        await db_session.commit()
        
        # Mock embedding search
        with patch("app.langchain.embeddings.EmbeddingService.search_similar") as mock_search:
            mock_search.return_value = []
            
            with patch("app.langchain.config.get_llm") as mock_get_llm:
                mock_llm = MagicMock()
                mock_response = MagicMock()
                mock_response.content = "The candidate has a Bachelor's degree."
                mock_llm.invoke = MagicMock(return_value=mock_response)
                mock_get_llm.return_value = mock_llm
                
                response = await client.post(
                    f"/api/chat/{test_cv.id}/explain/EDUCATION",  # Uppercase
                    headers=auth_headers,
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["criterion"].lower() == "education"
    
    @pytest.mark.asyncio
    async def test_explain_criterion_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
    ):
        """Should return 404 for non-existent criterion."""
        evaluation = CVEvaluation(
            id=uuid.uuid4(),
            cv_id=test_cv.id,
            template_id=None,
            score=75,
            status="pass",
            reasoning="Good",
            criteria_results={
                "Education": {"score": 10, "max_score": 15, "met": True, "feedback": "Ok"},
            },
        )
        db_session.add(evaluation)
        await db_session.commit()
        
        response = await client.post(
            f"/api/chat/{test_cv.id}/explain/NonExistent",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_explain_criterion_cv_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Should return 404 for non-existent CV."""
        fake_cv_id = uuid.uuid4()
        
        response = await client.post(
            f"/api/chat/{fake_cv_id}/explain/Education",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_explain_criterion_no_evaluation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_user: User,
    ):
        """Should return error when CV has no evaluation."""
        # Create CV without evaluation
        cv = CV(
            id=uuid.uuid4(),
            user_id=test_user.id,
            filename="no_eval.pdf",
            original_text="Some text",
            candidate_name="No Eval",
            status="pending",
        )
        db_session.add(cv)
        await db_session.commit()
        
        response = await client.post(
            f"/api/chat/{cv.id}/explain/Education",
            headers=auth_headers,
        )
        
        # Either 400 (bad request - no evaluation) or 404 (not found) is acceptable
        assert response.status_code in [400, 404]
    
    @pytest.mark.asyncio
    async def test_explain_criterion_unauthorized(
        self,
        client: AsyncClient,
        test_cv: CV,
    ):
        """Should return 401 without auth token."""
        response = await client.post(
            f"/api/chat/{test_cv.id}/explain/Education"
        )
        
        assert response.status_code == 401


# =============================================================================
# Test: POST /api/chat/compare - Compare CVs
# =============================================================================

class TestCompareCVs:
    """Tests for the compare CVs endpoint."""
    
    @pytest.mark.asyncio
    async def test_compare_cvs_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
        test_cv_2: CV,
    ):
        """Should compare two CVs successfully."""
        # Mock embedding search
        with patch("app.langchain.embeddings.EmbeddingService.search_similar") as mock_search:
            mock_search.return_value = []
            
            with patch("app.langchain.config.get_llm") as mock_get_llm:
                mock_llm = AsyncMock()
                mock_response = MagicMock()
                mock_response.content = "John Doe has more Python experience, while Jane Smith has stronger ML skills."
                mock_llm.ainvoke = AsyncMock(return_value=mock_response)
                mock_get_llm.return_value = mock_llm
                
                response = await client.post(
                    "/api/chat/compare",
                    json={
                        "cv_ids": [str(test_cv.id), str(test_cv_2.id)],
                        "question": "Compare their Python experience",
                    },
                    headers=auth_headers,
                )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["cv_ids"]) == 2
        assert "comparison" in data
    
    @pytest.mark.asyncio
    async def test_compare_cvs_too_few(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_cv: CV,
    ):
        """Should return 422 for fewer than 2 CVs."""
        response = await client.post(
            "/api/chat/compare",
            json={
                "cv_ids": [str(test_cv.id)],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_compare_cvs_too_many(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Should return 422 for more than 5 CVs."""
        cv_ids = [str(uuid.uuid4()) for _ in range(6)]
        
        response = await client.post(
            "/api/chat/compare",
            json={"cv_ids": cv_ids},
            headers=auth_headers,
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_compare_cvs_one_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_cv: CV,
    ):
        """Should return 404 when one CV doesn't exist."""
        fake_cv_id = uuid.uuid4()
        
        response = await client.post(
            "/api/chat/compare",
            json={
                "cv_ids": [str(test_cv.id), str(fake_cv_id)],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_compare_cvs_other_user_cv(
        self,
        client: AsyncClient,
        db_session,
        test_cv: CV,
        test_user_2: User,
    ):
        """Should return 403/404 when comparing with another user's CV."""
        from app.core.security import create_access_token
        
        # Create CV owned by user2
        other_cv = CV(
            id=uuid.uuid4(),
            user_id=test_user_2.id,
            filename="other.pdf",
            original_text="Other CV content",
            candidate_name="Other Person",
            status="evaluated",
        )
        db_session.add(other_cv)
        await db_session.commit()
        
        # test_user trying to compare with test_user_2's CV
        from app.core.security import create_access_token
        from app.db.models.user import User
        
        # Get test_user (owner of test_cv)
        token = create_access_token(str(test_cv.user_id))
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.post(
            "/api/chat/compare",
            json={
                "cv_ids": [str(test_cv.id), str(other_cv.id)],
            },
            headers=headers,
        )
        
        # Should fail because other_cv belongs to test_user_2
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_compare_cvs_default_question(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_cv: CV,
        test_cv_2: CV,
    ):
        """Should use default question when none provided."""
        # Mock embedding search
        with patch("app.langchain.embeddings.EmbeddingService.search_similar") as mock_search:
            mock_search.return_value = []
            
            with patch("app.langchain.config.get_llm") as mock_get_llm:
                mock_llm = AsyncMock()
                mock_response = MagicMock()
                mock_response.content = "Overall comparison..."
                mock_llm.ainvoke = AsyncMock(return_value=mock_response)
                mock_get_llm.return_value = mock_llm
                
                response = await client.post(
                    "/api/chat/compare",
                    json={
                        "cv_ids": [str(test_cv.id), str(test_cv_2.id)],
                        # No question provided - uses default
                    },
                    headers=auth_headers,
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "comparison" in data
    
    @pytest.mark.asyncio
    async def test_compare_cvs_unauthorized(
        self,
        client: AsyncClient,
        test_cv: CV,
        test_cv_2: CV,
    ):
        """Should return 401 without auth token."""
        response = await client.post(
            "/api/chat/compare",
            json={
                "cv_ids": [str(test_cv.id), str(test_cv_2.id)],
            },
        )
        
        assert response.status_code == 401
