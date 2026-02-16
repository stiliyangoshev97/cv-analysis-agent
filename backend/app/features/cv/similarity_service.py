"""Vector similarity search service for CV comparison.

This module provides the SimilarityService class for finding similar CVs
using vector embeddings and pgvector similarity search.

Features:
    - Find CVs similar to a given CV
    - Calculate percentile ranking among all CVs
    - Compare specific CVs head-to-head
    - Search CVs by natural language query

Classes:
    SimilarityService: Vector similarity search operations.
    SimilarCVResult: Result from similarity search.
    CVRankingResult: Percentile ranking result.
    CVComparisonResult: Head-to-head comparison result.

Example:
    Using the service::
    
        service = SimilarityService(session)
        
        # Find similar CVs
        similar = await service.find_similar_cvs(cv_id, user_id, limit=5)
        
        # Get ranking
        ranking = await service.get_cv_ranking(cv_id, user_id)
        print(f"Top {ranking.percentile}% of candidates")
"""

import uuid
import logging
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cv import CV, CVEvaluation
from app.langchain.embeddings import embed_text
from .cv_repository import CVRepository
from .embedding_repository import EmbeddingRepository
from .evaluation_repository import EvaluationRepository

logger = logging.getLogger(__name__)


@dataclass
class SimilarCVResult:
    """Result from CV similarity search.
    
    Attributes:
        cv_id: UUID of the similar CV.
        filename: Original filename of the CV.
        candidate_name: Name extracted from CV (if available).
        similarity_score: Cosine similarity (0-1, higher = more similar).
        evaluation_score: CV evaluation score (if evaluated).
        status: Pass/fail status (if evaluated).
    
    Example:
        >>> for result in similar_cvs:
        ...     print(f"{result.candidate_name}: {result.similarity_score:.1%} similar")
    """
    cv_id: uuid.UUID
    filename: str
    candidate_name: Optional[str]
    similarity_score: float
    evaluation_score: Optional[int]
    status: Optional[str]


@dataclass
class CVRankingResult:
    """Percentile ranking result for a CV.
    
    Attributes:
        cv_id: UUID of the ranked CV.
        percentile: Percentile rank (0-100, higher = better).
        rank: Absolute rank (1 = best).
        total_cvs: Total number of CVs in comparison.
        evaluation_score: This CV's evaluation score.
        average_score: Average score across all CVs.
        highest_score: Highest score in the dataset.
    
    Example:
        >>> ranking = await service.get_cv_ranking(cv_id, user_id)
        >>> print(f"Ranked #{ranking.rank} of {ranking.total_cvs}")
        >>> print(f"Top {100 - ranking.percentile:.0f}% of candidates")
    """
    cv_id: uuid.UUID
    percentile: float
    rank: int
    total_cvs: int
    evaluation_score: int
    average_score: float
    highest_score: int


@dataclass
class CVComparisonItem:
    """Single CV in a comparison.
    
    Attributes:
        cv_id: UUID of the CV.
        filename: Original filename.
        candidate_name: Candidate name (if available).
        evaluation_score: Evaluation score.
        status: Pass/fail status.
        similarity_to_first: Similarity to the first CV in comparison.
    """
    cv_id: uuid.UUID
    filename: str
    candidate_name: Optional[str]
    evaluation_score: Optional[int]
    status: Optional[str]
    similarity_to_first: float


@dataclass
class CVComparisonResult:
    """Result from comparing multiple CVs.
    
    Attributes:
        cvs: List of compared CVs with details.
        similarity_matrix: NxN matrix of pairwise similarities.
        best_match_id: UUID of the highest-scoring CV.
        most_similar_pair: Tuple of (cv_id_1, cv_id_2, similarity).
    
    Example:
        >>> comparison = await service.compare_cvs(cv_ids, user_id)
        >>> print(f"Best candidate: {comparison.best_match_id}")
    """
    cvs: List[CVComparisonItem]
    similarity_matrix: List[List[float]]
    best_match_id: Optional[uuid.UUID]
    most_similar_pair: Optional[tuple]


class SimilarityService:
    """Service for vector similarity search on CVs.
    
    Uses pgvector cosine similarity to find similar CVs,
    calculate rankings, and compare candidates.
    
    Attributes:
        session: AsyncSession for database operations.
        cv_repo: Repository for CV operations.
        embedding_repo: Repository for embedding operations.
        evaluation_repo: Repository for evaluation operations.
    
    Authorization:
        All methods require user_id to enforce multi-tenancy.
        Users can only search/compare their own CVs.
    
    Example:
        >>> service = SimilarityService(session)
        >>> similar = await service.find_similar_cvs(cv_id, user_id)
        >>> for cv in similar:
        ...     print(f"{cv.candidate_name}: {cv.similarity_score:.1%}")
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session.
        
        Args:
            session: SQLAlchemy AsyncSession.
        """
        self.session = session
        self.cv_repo = CVRepository(session)
        self.embedding_repo = EmbeddingRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
    
    async def find_similar_cvs(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 5,
        min_similarity: float = 0.3,
    ) -> List[SimilarCVResult]:
        """Find CVs similar to a given CV.
        
        Uses the average embedding of all chunks in the source CV
        to find similar CVs in the user's collection.
        
        Args:
            cv_id: Source CV's UUID.
            user_id: User's UUID for authorization.
            limit: Maximum number of similar CVs to return.
            min_similarity: Minimum similarity threshold (0-1, default 0.3).
            
        Returns:
            List of SimilarCVResult sorted by similarity (descending).
            
        Raises:
            ValueError: If CV not found or not owned by user.
        
        Example:
            >>> similar = await service.find_similar_cvs(cv_id, user_id, limit=5)
            >>> for cv in similar:
            ...     print(f"{cv.candidate_name}: {cv.similarity_score:.1%} similar")
        """
        # Verify CV ownership
        source_cv = await self.cv_repo.get_by_id(cv_id)
        if not source_cv or source_cv.user_id != user_id:
            raise ValueError("CV not found or access denied")
        
        # Get source CV embeddings
        source_embeddings = await self.embedding_repo.get_by_cv(cv_id)
        if not source_embeddings:
            raise ValueError("CV has no embeddings - please re-process")
        
        # Calculate average embedding for the source CV
        avg_embedding = self._calculate_average_embedding(
            [emb.embedding for emb in source_embeddings]
        )
        
        # Search for similar embeddings across all user's CVs
        similar_results = await self.embedding_repo.search_similar_all(
            query_vector=avg_embedding,
            limit=limit * 10,  # Get more to filter and deduplicate
            user_id=user_id,
        )
        
        # Group by CV and calculate average similarity per CV
        cv_similarities: dict[uuid.UUID, list[float]] = {}
        for result in similar_results:
            if result.embedding.cv_id != cv_id:  # Exclude source CV
                cv_similarities.setdefault(result.embedding.cv_id, []).append(
                    result.similarity
                )
        
        # Calculate average similarity per CV
        cv_avg_similarities = {
            cv_id: sum(sims) / len(sims)
            for cv_id, sims in cv_similarities.items()
        }
        
        # Sort by similarity and limit
        sorted_cv_ids = sorted(
            cv_avg_similarities.keys(),
            key=lambda x: cv_avg_similarities[x],
            reverse=True,
        )[:limit]
        
        # Fetch CV details and evaluations
        results = []
        for similar_cv_id in sorted_cv_ids:
            similarity = cv_avg_similarities[similar_cv_id]
            
            if similarity < min_similarity:
                continue
            
            cv = await self.cv_repo.get_by_id(similar_cv_id)
            if not cv:
                continue
            
            evaluation = await self.evaluation_repo.get_latest_by_cv(similar_cv_id)
            
            results.append(SimilarCVResult(
                cv_id=similar_cv_id,
                filename=cv.filename,
                candidate_name=cv.candidate_name,
                similarity_score=similarity,
                evaluation_score=evaluation.score if evaluation else None,
                status=evaluation.status if evaluation else None,
            ))
        
        logger.info(f"Found {len(results)} similar CVs for CV {cv_id}")
        return results
    
    async def get_cv_ranking(
        self,
        cv_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CVRankingResult:
        """Get percentile ranking for a CV among user's CVs.
        
        Ranks based on evaluation score, not similarity.
        
        Args:
            cv_id: CV's UUID to rank.
            user_id: User's UUID for authorization.
            
        Returns:
            CVRankingResult with percentile and rank info.
            
        Raises:
            ValueError: If CV not found, not evaluated, or not owned by user.
        
        Example:
            >>> ranking = await service.get_cv_ranking(cv_id, user_id)
            >>> print(f"Top {100 - ranking.percentile:.0f}% of candidates")
        """
        # Verify CV ownership
        cv = await self.cv_repo.get_by_id(cv_id)
        if not cv or cv.user_id != user_id:
            raise ValueError("CV not found or access denied")
        
        # Get this CV's evaluation
        evaluation = await self.evaluation_repo.get_latest_by_cv(cv_id)
        if not evaluation:
            raise ValueError("CV has not been evaluated")
        
        # Get all evaluations for user's CVs
        all_evaluations = await self._get_all_user_evaluations(user_id)
        
        if len(all_evaluations) == 0:
            raise ValueError("No evaluations found for comparison")
        
        # Sort by score descending
        sorted_scores = sorted(
            [(e.cv_id, e.score) for e in all_evaluations],
            key=lambda x: x[1],
            reverse=True,
        )
        
        # Find rank (1-indexed)
        rank = next(
            (i + 1 for i, (cid, _) in enumerate(sorted_scores) if cid == cv_id),
            len(sorted_scores),
        )
        
        total = len(sorted_scores)
        scores = [s for _, s in sorted_scores]
        
        # Calculate percentile (percentage of CVs scored lower)
        lower_count = sum(1 for s in scores if s < evaluation.score)
        percentile = (lower_count / total) * 100 if total > 0 else 0
        
        return CVRankingResult(
            cv_id=cv_id,
            percentile=percentile,
            rank=rank,
            total_cvs=total,
            evaluation_score=evaluation.score,
            average_score=sum(scores) / len(scores) if scores else 0,
            highest_score=max(scores) if scores else 0,
        )
    
    async def compare_cvs(
        self,
        cv_ids: List[uuid.UUID],
        user_id: uuid.UUID,
    ) -> CVComparisonResult:
        """Compare multiple CVs head-to-head.
        
        Returns similarity matrix and comparison details.
        
        Args:
            cv_ids: List of CV UUIDs to compare (2-10).
            user_id: User's UUID for authorization.
            
        Returns:
            CVComparisonResult with comparison details.
            
        Raises:
            ValueError: If fewer than 2 CVs, or any CV not found/owned by user.
        
        Example:
            >>> comparison = await service.compare_cvs(cv_ids, user_id)
            >>> print(f"Best: {comparison.best_match_id}")
            >>> print(f"Most similar pair: {comparison.most_similar_pair}")
        """
        if len(cv_ids) < 2:
            raise ValueError("Need at least 2 CVs to compare")
        
        if len(cv_ids) > 10:
            raise ValueError("Cannot compare more than 10 CVs at once")
        
        # Verify all CVs exist and are owned by user
        cvs = []
        for cv_id in cv_ids:
            cv = await self.cv_repo.get_by_id(cv_id)
            if not cv or cv.user_id != user_id:
                raise ValueError(f"CV {cv_id} not found or access denied")
            cvs.append(cv)
        
        # Get embeddings for all CVs
        cv_embeddings: dict[uuid.UUID, list[float]] = {}
        for cv in cvs:
            embeddings = await self.embedding_repo.get_by_cv(cv.id)
            if embeddings:
                cv_embeddings[cv.id] = self._calculate_average_embedding(
                    [emb.embedding for emb in embeddings]
                )
            else:
                cv_embeddings[cv.id] = []
        
        # Calculate pairwise similarity matrix
        n = len(cvs)
        similarity_matrix = [[0.0] * n for _ in range(n)]
        most_similar_pair = None
        max_similarity = -1.0
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                elif cv_embeddings[cvs[i].id] and cv_embeddings[cvs[j].id]:
                    sim = self._cosine_similarity(
                        cv_embeddings[cvs[i].id],
                        cv_embeddings[cvs[j].id],
                    )
                    similarity_matrix[i][j] = sim
                    
                    if i < j and sim > max_similarity:
                        max_similarity = sim
                        most_similar_pair = (cvs[i].id, cvs[j].id, sim)
        
        # Build comparison items
        comparison_items = []
        best_score = -1
        best_match_id = None
        
        for i, cv in enumerate(cvs):
            evaluation = await self.evaluation_repo.get_latest_by_cv(cv.id)
            
            item = CVComparisonItem(
                cv_id=cv.id,
                filename=cv.filename,
                candidate_name=cv.candidate_name,
                evaluation_score=evaluation.score if evaluation else None,
                status=evaluation.status if evaluation else None,
                similarity_to_first=similarity_matrix[0][i],
            )
            comparison_items.append(item)
            
            if evaluation and evaluation.score > best_score:
                best_score = evaluation.score
                best_match_id = cv.id
        
        logger.info(f"Compared {len(cvs)} CVs for user {user_id}")
        
        return CVComparisonResult(
            cvs=comparison_items,
            similarity_matrix=similarity_matrix,
            best_match_id=best_match_id,
            most_similar_pair=most_similar_pair,
        )
    
    async def search_by_query(
        self,
        query: str,
        user_id: uuid.UUID,
        limit: int = 10,
        min_similarity: float = 0.0,
    ) -> List[SimilarCVResult]:
        """Search CVs by natural language query.
        
        Embeds the query and finds similar CV chunks.
        
        Args:
            query: Natural language search query.
            user_id: User's UUID for authorization.
            limit: Maximum number of results.
            min_similarity: Minimum similarity threshold.
            
        Returns:
            List of SimilarCVResult matching the query.
        
        Example:
            >>> results = await service.search_by_query(
            ...     "Python developer with fintech experience",
            ...     user_id,
            ...     limit=10,
            ... )
        """
        # Embed the query
        query_vector = await embed_text(query)
        
        # Search across all user's CVs
        similar_results = await self.embedding_repo.search_similar_all(
            query_vector=query_vector,
            limit=limit * 5,  # Get more to deduplicate
            user_id=user_id,
        )
        
        # Group by CV and calculate average similarity
        cv_similarities: dict[uuid.UUID, list[float]] = {}
        for result in similar_results:
            cv_similarities.setdefault(result.embedding.cv_id, []).append(
                result.similarity
            )
        
        # Calculate max similarity per CV (best matching chunk)
        cv_max_similarities = {
            cv_id: max(sims)
            for cv_id, sims in cv_similarities.items()
        }
        
        # Sort and limit
        sorted_cv_ids = sorted(
            cv_max_similarities.keys(),
            key=lambda x: cv_max_similarities[x],
            reverse=True,
        )[:limit]
        
        # Fetch details
        results = []
        for cv_id in sorted_cv_ids:
            similarity = cv_max_similarities[cv_id]
            
            if similarity < min_similarity:
                continue
            
            cv = await self.cv_repo.get_by_id(cv_id)
            if not cv:
                continue
            
            evaluation = await self.evaluation_repo.get_latest_by_cv(cv_id)
            
            results.append(SimilarCVResult(
                cv_id=cv_id,
                filename=cv.filename,
                candidate_name=cv.candidate_name,
                similarity_score=similarity,
                evaluation_score=evaluation.score if evaluation else None,
                status=evaluation.status if evaluation else None,
            ))
        
        logger.info(f"Search query '{query[:50]}...' found {len(results)} CVs")
        return results
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _calculate_average_embedding(
        self,
        embeddings: List[list],
    ) -> List[float]:
        """Calculate average of multiple embeddings.
        
        Args:
            embeddings: List of embedding vectors.
            
        Returns:
            Average embedding vector.
        """
        if not embeddings:
            return []
        
        n = len(embeddings)
        dim = len(embeddings[0])
        
        avg = [0.0] * dim
        for emb in embeddings:
            for i in range(dim):
                avg[i] += emb[i]
        
        return [v / n for v in avg]
    
    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float],
    ) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First embedding vector.
            vec2: Second embedding vector.
            
        Returns:
            Cosine similarity (-1 to 1, higher = more similar).
        """
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _get_all_user_evaluations(
        self,
        user_id: uuid.UUID,
    ) -> List[CVEvaluation]:
        """Get all evaluations for a user's CVs.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            List of CVEvaluation entities.
        """
        result = await self.session.execute(
            select(CVEvaluation)
            .join(CV, CVEvaluation.cv_id == CV.id)
            .where(CV.user_id == user_id)
        )
        return list(result.scalars().all())
