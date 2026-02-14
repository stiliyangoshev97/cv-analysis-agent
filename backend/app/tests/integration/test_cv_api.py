"""Integration tests for CV API endpoints.

Tests:
    - GET /api/cv/ - List CVs
    - GET /api/cv/{id} - Get CV details
    - DELETE /api/cv/{id} - Delete CV
    - GET /api/cv/{id}/similar - Find similar CVs
    - GET /api/cv/{id}/ranking - Get CV ranking
    - POST /api/cv/compare - Compare CVs
    - POST /api/cv/search - Semantic search

Run with: pytest app/tests/integration/test_cv_api.py -v

API Schema Notes:
    - CVListResponse: {"cvs": [...], "total": N, "limit": N, "offset": N}
    - Delete returns 200 with {"message": "..."} (not 204)

Note:
    OpenAI embeddings are mocked in conftest.py's client fixture.
"""

import uuid
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.cv
class TestListCVsEndpoint:
    """Tests for GET /api/cv/."""
    
    async def test_list_cvs_empty(self, client, auth_headers):
        """Should return empty list when no CVs."""
        response = await client.get("/api/cv/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # CVListResponse uses "cvs" not "items"
        assert data["cvs"] == []
        assert data["total"] == 0
    
    async def test_list_cvs_with_data(self, client, auth_headers, test_cv):
        """Should return list of user's CVs."""
        response = await client.get("/api/cv/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["cvs"]) == 1
        assert data["cvs"][0]["id"] == str(test_cv.id)
    
    async def test_list_cvs_unauthorized(self, client):
        """Should return 401 without auth."""
        response = await client.get("/api/cv/")
        
        assert response.status_code == 401
    
    async def test_list_cvs_pagination(self, client, auth_headers, test_cv, test_cv_2):
        """Should support pagination."""
        response = await client.get(
            "/api/cv/",
            params={"limit": 1, "offset": 0},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["cvs"]) == 1
        assert data["total"] == 2


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.cv
class TestGetCVEndpoint:
    """Tests for GET /api/cv/{id}."""
    
    async def test_get_cv_success(self, client, auth_headers, test_cv):
        """Should return CV details."""
        response = await client.get(
            f"/api/cv/{test_cv.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_cv.id)
        assert data["filename"] == test_cv.filename
    
    async def test_get_cv_not_found(self, client, auth_headers):
        """Should return 404 for non-existent CV."""
        response = await client.get(
            f"/api/cv/{uuid.uuid4()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    async def test_get_cv_other_user(self, client, test_cv):
        """Should return 401 when token is for non-existent user."""
        # Create token for a user that doesn't exist in database
        from app.core.security import create_access_token
        
        # create_access_token takes user_id string directly
        other_token = create_access_token(str(uuid.uuid4()))
        headers = {"Authorization": f"Bearer {other_token}"}
        
        response = await client.get(
            f"/api/cv/{test_cv.id}",
            headers=headers,
        )
        
        # Returns 401 because the user in the token doesn't exist
        assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.cv
class TestDeleteCVEndpoint:
    """Tests for DELETE /api/cv/{id}."""
    
    async def test_delete_cv_success(self, client, auth_headers, test_cv):
        """Should delete CV successfully."""
        response = await client.delete(
            f"/api/cv/{test_cv.id}",
            headers=auth_headers,
        )
        
        # Controller returns 200 with message dict
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify deleted
        get_response = await client.get(
            f"/api/cv/{test_cv.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
    
    async def test_delete_cv_not_found(self, client, auth_headers):
        """Should return 404 for non-existent CV."""
        response = await client.delete(
            f"/api/cv/{uuid.uuid4()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.cv
class TestSimilarCVsEndpoint:
    """Tests for GET /api/cv/{id}/similar."""
    
    async def test_similar_cvs_not_found(self, client, auth_headers):
        """Should return 404 for non-existent CV."""
        response = await client.get(
            f"/api/cv/{uuid.uuid4()}/similar",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    async def test_similar_cvs_no_embeddings(self, client, auth_headers, test_cv):
        """Should return 400 when CV has no embeddings."""
        response = await client.get(
            f"/api/cv/{test_cv.id}/similar",
            headers=auth_headers,
        )
        
        # Should return error about no embeddings
        assert response.status_code in [400, 404]
    
    async def test_similar_cvs_success(
        self, client, auth_headers, test_cv, test_embedding
    ):
        """Should return similar CVs (mocked because pgvector not available in SQLite)."""
        # Mock the similarity service's find_similar_cvs method
        mock_similar_result = []  # Empty list = no similar CVs found
        
        with patch(
            "app.features.cv.similarity_service.SimilarityService.find_similar_cvs",
            return_value=mock_similar_result
        ):
            response = await client.get(
                f"/api/cv/{test_cv.id}/similar",
                params={"limit": 5},
                headers=auth_headers,
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "similar_cvs" in data


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.cv
class TestCVRankingEndpoint:
    """Tests for GET /api/cv/{id}/ranking."""
    
    async def test_ranking_not_evaluated(self, client, auth_headers, test_cv):
        """Should return error when CV not evaluated."""
        response = await client.get(
            f"/api/cv/{test_cv.id}/ranking",
            headers=auth_headers,
        )
        
        assert response.status_code in [400, 404]
    
    async def test_ranking_success(
        self, client, auth_headers, test_cv, test_evaluation
    ):
        """Should return ranking for evaluated CV."""
        response = await client.get(
            f"/api/cv/{test_cv.id}/ranking",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "percentile" in data
        assert "rank" in data
        assert "total_cvs" in data


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.cv
class TestCompareCVsEndpoint:
    """Tests for POST /api/cv/compare."""
    
    async def test_compare_too_few(self, client, auth_headers, test_cv):
        """Should return 422 for fewer than 2 CVs (validation error)."""
        response = await client.post(
            "/api/cv/compare",
            json={"cv_ids": [str(test_cv.id)]},
            headers=auth_headers,
        )
        
        # Pydantic validation returns 422, not 400
        assert response.status_code == 422
    
    async def test_compare_success(
        self, client, auth_headers, test_cv, test_cv_2, test_embedding
    ):
        """Should compare CVs successfully (mocked because pgvector not available in SQLite)."""
        from app.features.cv.similarity_service import CVComparisonResult, CVComparisonItem
        
        # Mock the similarity service's compare_cvs method
        mock_compare_result = CVComparisonResult(
            cvs=[
                CVComparisonItem(
                    cv_id=test_cv.id,
                    filename="test.pdf",
                    candidate_name="Test Candidate",
                    evaluation_score=75,
                    status="pass",
                    similarity_to_first=1.0,
                ),
                CVComparisonItem(
                    cv_id=test_cv_2.id,
                    filename="test2.pdf",
                    candidate_name="Second Candidate",
                    evaluation_score=80,
                    status="pass",
                    similarity_to_first=0.75,
                ),
            ],
            similarity_matrix=[[1.0, 0.75], [0.75, 1.0]],
            best_match_id=test_cv_2.id,
            most_similar_pair=(test_cv.id, test_cv_2.id, 0.75),
        )
        
        with patch(
            "app.features.cv.similarity_service.SimilarityService.compare_cvs",
            return_value=mock_compare_result
        ):
            response = await client.post(
                "/api/cv/compare",
                json={"cv_ids": [str(test_cv.id), str(test_cv_2.id)]},
                headers=auth_headers,
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "cvs" in data
        assert "similarity_matrix" in data


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.cv
class TestSearchCVsEndpoint:
    """Tests for POST /api/cv/search."""
    
    async def test_search_empty_query(self, client, auth_headers):
        """Should return 422 for empty query."""
        response = await client.post(
            "/api/cv/search",
            json={"query": ""},
            headers=auth_headers,
        )
        
        assert response.status_code == 422
    
    async def test_search_success(self, client, auth_headers, mock_openai_embeddings):
        """Should search CVs successfully."""
        with patch("app.features.cv.embedding_repository.EmbeddingRepository.search_similar_all") as mock:
            mock.return_value = []
            
            response = await client.post(
                "/api/cv/search",
                json={
                    "query": "Python developer with ML experience",
                    "limit": 10,
                },
                headers=auth_headers,
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
