"""Unit tests for SimilarityService.

Tests vector similarity search functionality including:
    - Finding similar CVs
    - Calculating percentile rankings
    - Comparing multiple CVs
    - Semantic search by query

Run with: pytest app/tests/unit/test_similarity_service.py -v
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.features.cv.similarity_service import (
    SimilarityService,
    SimilarCVResult,
    CVRankingResult,
    CVComparisonResult,
    CVComparisonItem,
)


class TestSimilarityServiceHelpers:
    """Tests for SimilarityService helper methods."""
    
    def test_calculate_average_embedding_single(self):
        """Should return same embedding when only one provided."""
        service = SimilarityService(MagicMock())
        
        embedding = [0.1, 0.2, 0.3, 0.4]
        result = service._calculate_average_embedding([embedding])
        
        assert result == embedding
    
    def test_calculate_average_embedding_multiple(self):
        """Should calculate element-wise average."""
        service = SimilarityService(MagicMock())
        
        embeddings = [
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
        ]
        result = service._calculate_average_embedding(embeddings)
        
        assert result == [2.0, 3.0, 4.0]
    
    def test_calculate_average_embedding_empty(self):
        """Should return empty list for empty input."""
        service = SimilarityService(MagicMock())
        
        result = service._calculate_average_embedding([])
        
        assert result == []
    
    def test_cosine_similarity_identical(self):
        """Should return 1.0 for identical vectors."""
        service = SimilarityService(MagicMock())
        
        vec = [0.5, 0.5, 0.5]
        result = service._cosine_similarity(vec, vec)
        
        assert abs(result - 1.0) < 0.0001
    
    def test_cosine_similarity_orthogonal(self):
        """Should return 0.0 for orthogonal vectors."""
        service = SimilarityService(MagicMock())
        
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        result = service._cosine_similarity(vec1, vec2)
        
        assert abs(result) < 0.0001
    
    def test_cosine_similarity_opposite(self):
        """Should return -1.0 for opposite vectors."""
        service = SimilarityService(MagicMock())
        
        vec1 = [1.0, 0.0]
        vec2 = [-1.0, 0.0]
        result = service._cosine_similarity(vec1, vec2)
        
        assert abs(result - (-1.0)) < 0.0001
    
    def test_cosine_similarity_empty(self):
        """Should return 0.0 for empty vectors."""
        service = SimilarityService(MagicMock())
        
        result = service._cosine_similarity([], [])
        
        assert result == 0.0
    
    def test_cosine_similarity_zero_vector(self):
        """Should return 0.0 when one vector is all zeros."""
        service = SimilarityService(MagicMock())
        
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        result = service._cosine_similarity(vec1, vec2)
        
        assert result == 0.0


@pytest.mark.asyncio
@pytest.mark.cv
class TestFindSimilarCVs:
    """Tests for find_similar_cvs method."""
    
    async def test_find_similar_cvs_not_found(self, db_session):
        """Should raise ValueError when CV not found."""
        service = SimilarityService(db_session)
        
        with pytest.raises(ValueError, match="CV not found"):
            await service.find_similar_cvs(
                cv_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
            )
    
    async def test_find_similar_cvs_wrong_user(self, db_session, test_cv, test_user_2):
        """Should raise ValueError when CV belongs to different user."""
        service = SimilarityService(db_session)
        
        with pytest.raises(ValueError, match="CV not found or access denied"):
            await service.find_similar_cvs(
                cv_id=test_cv.id,
                user_id=test_user_2.id,
            )
    
    async def test_find_similar_cvs_no_embeddings(self, db_session, test_cv, test_user):
        """Should raise ValueError when CV has no embeddings."""
        service = SimilarityService(db_session)
        
        # Mock repository to return empty embeddings
        with patch.object(service.embedding_repo, "get_by_cv") as mock_get:
            mock_get.return_value = []
            
            with pytest.raises(ValueError, match="CV has no embeddings"):
                await service.find_similar_cvs(
                    cv_id=test_cv.id,
                    user_id=test_user.id,
                )
    
    async def test_find_similar_cvs_success(
        self, db_session, test_cv, test_cv_2, test_user, test_embedding
    ):
        """Should find similar CVs successfully."""
        service = SimilarityService(db_session)
        
        # Mock the embedding repository methods
        mock_embedding = MagicMock()
        mock_embedding.embedding = [0.1] * 1536
        
        with patch.object(service.embedding_repo, "get_by_cv") as mock_get:
            mock_get.return_value = [mock_embedding]
            
            with patch.object(service.embedding_repo, "search_similar_all") as mock_search:
                mock_result = MagicMock()
                mock_result.embedding.cv_id = test_cv_2.id
                mock_result.similarity = 0.95
                mock_search.return_value = [mock_result]
                
                results = await service.find_similar_cvs(
                    cv_id=test_cv.id,
                    user_id=test_user.id,
                limit=5,
            )
        
        assert isinstance(results, list)


@pytest.mark.asyncio
@pytest.mark.cv
class TestGetCVRanking:
    """Tests for get_cv_ranking method."""
    
    async def test_get_ranking_cv_not_found(self, db_session):
        """Should raise ValueError when CV not found."""
        service = SimilarityService(db_session)
        
        with pytest.raises(ValueError, match="CV not found"):
            await service.get_cv_ranking(
                cv_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
            )
    
    async def test_get_ranking_not_evaluated(self, db_session, test_cv, test_user):
        """Should raise ValueError when CV has no evaluation."""
        service = SimilarityService(db_session)
        
        with pytest.raises(ValueError, match="CV has not been evaluated"):
            await service.get_cv_ranking(
                cv_id=test_cv.id,
                user_id=test_user.id,
            )
    
    async def test_get_ranking_success(
        self, db_session, test_cv, test_user, test_evaluation
    ):
        """Should return ranking when CV is evaluated."""
        service = SimilarityService(db_session)
        
        result = await service.get_cv_ranking(
            cv_id=test_cv.id,
            user_id=test_user.id,
        )
        
        assert isinstance(result, CVRankingResult)
        assert result.cv_id == test_cv.id
        assert result.rank == 1  # Only CV, so rank 1
        assert result.total_cvs == 1
        assert result.evaluation_score == 85
    
    async def test_get_ranking_percentile(self, db_session, test_user):
        """Should calculate correct percentile with multiple CVs."""
        from app.db.models.cv import CV, CVEvaluation
        
        # Create 5 CVs with different scores
        cvs = []
        for i, score in enumerate([60, 70, 80, 90, 100]):
            cv = CV(
                id=uuid.uuid4(),
                user_id=test_user.id,
                filename=f"cv_{i}.pdf",
                original_text=f"CV content {i}",
                status="evaluated",
            )
            db_session.add(cv)
            cvs.append((cv, score))
        
        await db_session.flush()
        
        for cv, score in cvs:
            evaluation = CVEvaluation(
                id=uuid.uuid4(),
                cv_id=cv.id,
                score=score,
                status="pass" if score >= 70 else "fail",
                reasoning=f"Score: {score}",
                criteria_results={},
            )
            db_session.add(evaluation)
        
        await db_session.commit()
        
        service = SimilarityService(db_session)
        
        # Check the CV with score 80 (middle)
        middle_cv = cvs[2][0]
        result = await service.get_cv_ranking(
            cv_id=middle_cv.id,
            user_id=test_user.id,
        )
        
        assert result.rank == 3  # 3rd highest
        assert result.total_cvs == 5
        assert result.percentile == 40.0  # 2 out of 5 scored lower (40%)
        assert result.highest_score == 100
        assert result.average_score == 80.0


@pytest.mark.asyncio
@pytest.mark.cv
class TestCompareCVs:
    """Tests for compare_cvs method."""
    
    async def test_compare_too_few_cvs(self, db_session, test_user):
        """Should raise ValueError when fewer than 2 CVs."""
        service = SimilarityService(db_session)
        
        with pytest.raises(ValueError, match="Need at least 2 CVs"):
            await service.compare_cvs(
                cv_ids=[uuid.uuid4()],
                user_id=test_user.id,
            )
    
    async def test_compare_too_many_cvs(self, db_session, test_user):
        """Should raise ValueError when more than 10 CVs."""
        service = SimilarityService(db_session)
        
        cv_ids = [uuid.uuid4() for _ in range(11)]
        
        with pytest.raises(ValueError, match="Cannot compare more than 10 CVs"):
            await service.compare_cvs(
                cv_ids=cv_ids,
                user_id=test_user.id,
            )
    
    async def test_compare_cv_not_found(self, db_session, test_cv, test_user):
        """Should raise ValueError when any CV not found."""
        service = SimilarityService(db_session)
        
        with pytest.raises(ValueError, match="not found or access denied"):
            await service.compare_cvs(
                cv_ids=[test_cv.id, uuid.uuid4()],
                user_id=test_user.id,
            )
    
    async def test_compare_success(
        self, db_session, test_cv, test_cv_2, test_user, test_evaluation
    ):
        """Should compare CVs successfully."""
        service = SimilarityService(db_session)
        
        # Mock embedding repository to return embeddings
        mock_embedding_1 = MagicMock()
        mock_embedding_1.embedding = [0.1] * 1536
        
        mock_embedding_2 = MagicMock()
        mock_embedding_2.embedding = [0.2] * 1536
        
        with patch.object(service.embedding_repo, "get_by_cv") as mock_get:
            def get_by_cv_side_effect(cv_id):
                if cv_id == test_cv.id:
                    return [mock_embedding_1]
                return [mock_embedding_2]
            
            mock_get.side_effect = get_by_cv_side_effect
            
            result = await service.compare_cvs(
                cv_ids=[test_cv.id, test_cv_2.id],
                user_id=test_user.id,
            )
        
        assert isinstance(result, CVComparisonResult)
        assert len(result.cvs) == 2
        assert len(result.similarity_matrix) == 2
        assert len(result.similarity_matrix[0]) == 2
        
        # Diagonal should be 1.0 (self-similarity)
        assert result.similarity_matrix[0][0] == 1.0
        assert result.similarity_matrix[1][1] == 1.0
        
        # Best match should be test_cv (has evaluation with score 85)
        assert result.best_match_id == test_cv.id


@pytest.mark.asyncio
@pytest.mark.cv
class TestSearchByQuery:
    """Tests for search_by_query method."""
    
    async def test_search_empty_results(self, db_session, test_user):
        """Should return empty list when no matches."""
        service = SimilarityService(db_session)
        
        with patch("app.features.cv.similarity_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.1] * 1536
            
            with patch.object(service.embedding_repo, "search_similar_all") as mock_search:
                mock_search.return_value = []
                
                results = await service.search_by_query(
                    query="Python developer",
                    user_id=test_user.id,
                )
        
        assert results == []
    
    async def test_search_returns_results(self, db_session, test_cv, test_user):
        """Should return matching CVs."""
        service = SimilarityService(db_session)
        
        with patch("app.features.cv.similarity_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.1] * 1536
            
            with patch.object(service.embedding_repo, "search_similar_all") as mock_search:
                mock_result = MagicMock()
                mock_result.embedding.cv_id = test_cv.id
                mock_result.similarity = 0.88
                mock_search.return_value = [mock_result]
                
                results = await service.search_by_query(
                    query="Python developer",
                    user_id=test_user.id,
                    limit=10,
                )
        
        assert len(results) == 1
        assert results[0].cv_id == test_cv.id
        assert results[0].similarity_score == 0.88
    
    async def test_search_respects_min_similarity(self, db_session, test_cv, test_user):
        """Should filter out results below min_similarity."""
        service = SimilarityService(db_session)
        
        with patch("app.features.cv.similarity_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.1] * 1536
            
            with patch.object(service.embedding_repo, "search_similar_all") as mock_search:
                mock_result = MagicMock()
                mock_result.embedding.cv_id = test_cv.id
                mock_result.similarity = 0.3  # Low similarity
                mock_search.return_value = [mock_result]
                
                results = await service.search_by_query(
                    query="Python developer",
                    user_id=test_user.id,
                    min_similarity=0.5,  # Threshold higher than result
                )
        
        assert results == []


class TestDataclasses:
    """Tests for result dataclasses."""
    
    def test_similar_cv_result_creation(self):
        """Should create SimilarCVResult correctly."""
        result = SimilarCVResult(
            cv_id=uuid.uuid4(),
            filename="test.pdf",
            candidate_name="John Doe",
            similarity_score=0.95,
            evaluation_score=85,
            status="pass",
        )
        
        assert result.filename == "test.pdf"
        assert result.similarity_score == 0.95
    
    def test_cv_ranking_result_creation(self):
        """Should create CVRankingResult correctly."""
        result = CVRankingResult(
            cv_id=uuid.uuid4(),
            percentile=80.0,
            rank=2,
            total_cvs=10,
            evaluation_score=85,
            average_score=75.0,
            highest_score=95,
        )
        
        assert result.percentile == 80.0
        assert result.rank == 2
    
    def test_cv_comparison_result_creation(self):
        """Should create CVComparisonResult correctly."""
        result = CVComparisonResult(
            cvs=[],
            similarity_matrix=[[1.0]],
            best_match_id=uuid.uuid4(),
            most_similar_pair=None,
        )
        
        assert result.similarity_matrix == [[1.0]]
