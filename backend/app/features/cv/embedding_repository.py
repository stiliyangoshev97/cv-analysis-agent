"""Embedding repository for database operations.

This module provides the EmbeddingRepository class for performing
database CRUD operations on CVEmbedding entities using SQLAlchemy.
Handles vector storage and similarity search via pgvector.

Classes:
    EmbeddingRepository: Async repository for embedding database operations.
    SimilarityResult: Named tuple for search results with scores.

Example:
    Using the repository::
    
        async with get_db_session() as session:
            repo = EmbeddingRepository(session)
            results = await repo.search_similar(cv_id, query_vector, limit=5)
"""

import uuid
from dataclasses import dataclass
from typing import Optional, List, Sequence

from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cv import CVEmbedding, CV


@dataclass
class SimilarityResult:
    """Search result with similarity score.
    
    Attributes:
        embedding: The CVEmbedding entity.
        distance: Cosine distance (0 = identical, 2 = opposite).
        similarity: Cosine similarity (1 = identical, -1 = opposite).
    """
    embedding: CVEmbedding
    distance: float
    similarity: float


class EmbeddingRepository:
    """Repository for CVEmbedding database operations.
    
    Provides async methods for CRUD operations on CVEmbedding entities
    and pgvector similarity search. This is the data access layer -
    use EmbeddingService for higher-level operations with LangChain.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = EmbeddingRepository(session)
        >>> embeddings = await repo.get_by_cv(cv_id)
        >>> for emb in embeddings:
        ...     print(f"Chunk {emb.chunk_index}: {emb.chunk_text[:50]}...")
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
    
    async def create(self, embedding: CVEmbedding) -> CVEmbedding:
        """Create a new embedding in the database.
        
        Args:
            embedding: CVEmbedding entity to persist.
            
        Returns:
            The persisted CVEmbedding entity with generated ID.
        """
        self.session.add(embedding)
        await self.session.flush()
        return embedding
    
    async def create_many(
        self,
        embeddings: List[CVEmbedding],
    ) -> List[CVEmbedding]:
        """Create multiple embeddings in a batch.
        
        More efficient than individual creates for bulk operations.
        
        Args:
            embeddings: List of CVEmbedding entities to persist.
            
        Returns:
            List of persisted CVEmbedding entities.
        """
        self.session.add_all(embeddings)
        await self.session.flush()
        return embeddings
    
    async def get_by_id(
        self,
        embedding_id: uuid.UUID,
    ) -> Optional[CVEmbedding]:
        """Get embedding by ID.
        
        Args:
            embedding_id: Embedding's UUID.
            
        Returns:
            CVEmbedding if found, None otherwise.
        """
        result = await self.session.execute(
            select(CVEmbedding).where(CVEmbedding.id == embedding_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_cv(
        self,
        cv_id: uuid.UUID,
        ordered: bool = True,
    ) -> List[CVEmbedding]:
        """Get all embeddings for a CV.
        
        Args:
            cv_id: CV's UUID.
            ordered: Whether to order by chunk_index.
            
        Returns:
            List of CVEmbedding entities.
        """
        query = select(CVEmbedding).where(CVEmbedding.cv_id == cv_id)
        
        if ordered:
            query = query.order_by(CVEmbedding.chunk_index)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_by_cv(self, cv_id: uuid.UUID) -> int:
        """Count embeddings for a CV.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            Number of embeddings for the CV.
        """
        result = await self.session.execute(
            select(func.count(CVEmbedding.id)).where(CVEmbedding.cv_id == cv_id)
        )
        return result.scalar() or 0
    
    async def delete_by_cv(self, cv_id: uuid.UUID) -> int:
        """Delete all embeddings for a CV.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            Number of embeddings deleted.
        """
        result = await self.session.execute(
            delete(CVEmbedding).where(CVEmbedding.cv_id == cv_id)
        )
        await self.session.flush()
        return result.rowcount or 0
    
    async def delete(self, embedding: CVEmbedding) -> None:
        """Delete a single embedding.
        
        Args:
            embedding: CVEmbedding entity to delete.
        """
        await self.session.delete(embedding)
        await self.session.flush()
    
    # --- Vector Search Operations ---
    
    async def search_similar_in_cv(
        self,
        cv_id: uuid.UUID,
        query_vector: List[float],
        limit: int = 5,
    ) -> List[SimilarityResult]:
        """Search for similar chunks within a specific CV.
        
        Uses cosine distance for similarity matching via pgvector.
        
        Args:
            cv_id: CV's UUID to search within.
            query_vector: Embedding vector of the search query.
            limit: Maximum number of results.
            
        Returns:
            List of SimilarityResult with embeddings and scores.
        
        Example:
            >>> query_vector = await embed_text("fintech experience")
            >>> results = await repo.search_similar_in_cv(cv_id, query_vector)
            >>> for r in results:
            ...     print(f"Score: {r.similarity:.3f} - {r.embedding.chunk_text[:50]}...")
        """
        # pgvector cosine distance: <=> operator
        distance_expr = CVEmbedding.embedding.cosine_distance(query_vector)
        
        result = await self.session.execute(
            select(CVEmbedding, distance_expr.label("distance"))
            .where(CVEmbedding.cv_id == cv_id)
            .order_by(distance_expr)
            .limit(limit)
        )
        
        return [
            SimilarityResult(
                embedding=row.CVEmbedding,
                distance=row.distance,
                similarity=1 - row.distance,  # Convert distance to similarity
            )
            for row in result.all()
        ]
    
    async def search_similar_all(
        self,
        query_vector: List[float],
        limit: int = 10,
        user_id: Optional[uuid.UUID] = None,
    ) -> List[SimilarityResult]:
        """Search for similar chunks across all CVs.
        
        Useful for finding candidates matching specific criteria.
        
        Args:
            query_vector: Embedding vector of the search query.
            limit: Maximum number of results.
            user_id: Optional user ID to filter CVs (multi-tenant).
            
        Returns:
            List of SimilarityResult from different CVs.
        
        Example:
            >>> query_vector = await embed_text("React developer with 5 years experience")
            >>> results = await repo.search_similar_all(query_vector, limit=10)
            >>> # Group by CV
            >>> by_cv = {}
            >>> for r in results:
            ...     by_cv.setdefault(r.embedding.cv_id, []).append(r)
        """
        distance_expr = CVEmbedding.embedding.cosine_distance(query_vector)
        
        query = (
            select(CVEmbedding, distance_expr.label("distance"))
            .order_by(distance_expr)
            .limit(limit)
        )
        
        # Filter by user if provided (requires join to CV table)
        if user_id is not None:
            query = (
                select(CVEmbedding, distance_expr.label("distance"))
                .join(CV, CVEmbedding.cv_id == CV.id)
                .where(CV.user_id == user_id)
                .order_by(distance_expr)
                .limit(limit)
            )
        
        result = await self.session.execute(query)
        
        return [
            SimilarityResult(
                embedding=row.CVEmbedding,
                distance=row.distance,
                similarity=1 - row.distance,
            )
            for row in result.all()
        ]
    
    async def search_by_threshold(
        self,
        cv_id: uuid.UUID,
        query_vector: List[float],
        max_distance: float = 0.5,
        limit: int = 20,
    ) -> List[SimilarityResult]:
        """Search for chunks within a distance threshold.
        
        Returns only chunks that are sufficiently similar.
        
        Args:
            cv_id: CV's UUID to search within.
            query_vector: Embedding vector of the search query.
            max_distance: Maximum cosine distance (0-2, lower = more similar).
            limit: Maximum number of results.
            
        Returns:
            List of SimilarityResult meeting the threshold.
        """
        distance_expr = CVEmbedding.embedding.cosine_distance(query_vector)
        
        result = await self.session.execute(
            select(CVEmbedding, distance_expr.label("distance"))
            .where(
                and_(
                    CVEmbedding.cv_id == cv_id,
                    distance_expr <= max_distance,
                )
            )
            .order_by(distance_expr)
            .limit(limit)
        )
        
        return [
            SimilarityResult(
                embedding=row.CVEmbedding,
                distance=row.distance,
                similarity=1 - row.distance,
            )
            for row in result.all()
        ]
    
    async def get_chunk_texts(
        self,
        cv_id: uuid.UUID,
    ) -> List[str]:
        """Get just the text content of all chunks for a CV.
        
        Useful when you don't need the vectors, just the text.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            List of chunk texts in order.
        """
        result = await self.session.execute(
            select(CVEmbedding.chunk_text)
            .where(CVEmbedding.cv_id == cv_id)
            .order_by(CVEmbedding.chunk_index)
        )
        return list(result.scalars().all())
    
    async def exists_for_cv(self, cv_id: uuid.UUID) -> bool:
        """Check if embeddings exist for a CV.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            True if at least one embedding exists.
        """
        result = await self.session.execute(
            select(CVEmbedding.id).where(CVEmbedding.cv_id == cv_id).limit(1)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_embedding_model(self, cv_id: uuid.UUID) -> Optional[str]:
        """Get the embedding model used for a CV.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            Model name string if embeddings exist, None otherwise.
        """
        result = await self.session.execute(
            select(CVEmbedding.model)
            .where(CVEmbedding.cv_id == cv_id)
            .limit(1)
        )
        return result.scalar_one_or_none()
