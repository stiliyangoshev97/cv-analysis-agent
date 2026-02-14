"""
Embedding Generation and Storage

Handles generating embeddings from text and storing them in pgvector.
Provides both low-level embedding functions and high-level storage integration.
"""

import uuid
from typing import Sequence

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cv import CVEmbedding
from app.langchain.config import get_embeddings, get_langchain_settings


async def embed_text(
    text: str,
    embeddings_model: OpenAIEmbeddings | None = None,
) -> list[float]:
    """
    Generate an embedding vector for a single text.
    
    Args:
        text: The text to embed.
        embeddings_model: Optional pre-configured embeddings model.
    
    Returns:
        List of floats representing the embedding vector.
    
    Example:
        ```python
        vector = await embed_text("Senior React developer with fintech experience")
        print(len(vector))  # 1536
        ```
    """
    model = embeddings_model or get_embeddings()
    return await model.aembed_query(text)


async def embed_texts(
    texts: list[str],
    embeddings_model: OpenAIEmbeddings | None = None,
) -> list[list[float]]:
    """
    Generate embedding vectors for multiple texts.
    
    More efficient than calling embed_text multiple times
    as it batches the API requests.
    
    Args:
        texts: List of texts to embed.
        embeddings_model: Optional pre-configured embeddings model.
    
    Returns:
        List of embedding vectors (one per input text).
    
    Example:
        ```python
        texts = ["chunk 1 text", "chunk 2 text", "chunk 3 text"]
        vectors = await embed_texts(texts)
        print(len(vectors))  # 3
        print(len(vectors[0]))  # 1536
        ```
    """
    model = embeddings_model or get_embeddings()
    return await model.aembed_documents(texts)


async def embed_documents(
    documents: list[Document],
    embeddings_model: OpenAIEmbeddings | None = None,
) -> list[tuple[Document, list[float]]]:
    """
    Generate embeddings for LangChain Document objects.
    
    Returns documents paired with their embeddings for easy storage.
    
    Args:
        documents: List of LangChain Document objects.
        embeddings_model: Optional pre-configured embeddings model.
    
    Returns:
        List of (Document, embedding) tuples.
    
    Example:
        ```python
        from app.langchain.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        result = await processor.process_file("/path/to/cv.pdf")
        
        doc_embeddings = await embed_documents(result.chunks)
        for doc, embedding in doc_embeddings:
            print(f"Chunk: {doc.page_content[:50]}...")
            print(f"Embedding dim: {len(embedding)}")
        ```
    """
    texts = [doc.page_content for doc in documents]
    embeddings = await embed_texts(texts, embeddings_model)
    return list(zip(documents, embeddings))


class EmbeddingService:
    """
    High-level service for embedding generation and pgvector storage.
    
    Integrates with the database to store and search embeddings.
    
    Example:
        ```python
        service = EmbeddingService(session)
        
        # Store embeddings for a CV
        await service.store_cv_embeddings(cv_id, chunks)
        
        # Search for similar content
        results = await service.search_similar(cv_id, "fintech experience", limit=5)
        ```
    """
    
    def __init__(
        self,
        session: AsyncSession,
        embeddings_model: OpenAIEmbeddings | None = None,
        api_key: str | None = None,
    ):
        """
        Initialize the embedding service.
        
        Args:
            session: SQLAlchemy async session for database operations.
            embeddings_model: Optional pre-configured embeddings model.
            api_key: Optional OpenAI API key for BYOK (overrides system key).
        """
        self.session = session
        self.settings = get_langchain_settings()
        
        # Use provided model, or create one with provided API key
        if embeddings_model:
            self.embeddings_model = embeddings_model
        elif api_key:
            self.embeddings_model = get_embeddings(api_key=api_key)
        else:
            self.embeddings_model = get_embeddings()
    
    async def store_cv_embeddings(
        self,
        cv_id: uuid.UUID,
        chunks: list[Document] | list[str],
        replace_existing: bool = True,
    ) -> list[CVEmbedding]:
        """
        Generate and store embeddings for CV chunks.
        
        Args:
            cv_id: UUID of the CV these embeddings belong to.
            chunks: List of Document objects or raw text strings.
            replace_existing: If True, delete existing embeddings first.
        
        Returns:
            List of created CVEmbedding objects.
        
        Example:
            ```python
            from app.langchain.document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            result = await processor.process_file("/path/to/cv.pdf")
            
            embeddings = await service.store_cv_embeddings(cv.id, result.chunks)
            print(f"Stored {len(embeddings)} embeddings")
            ```
        """
        # Delete existing embeddings if requested
        if replace_existing:
            await self.delete_cv_embeddings(cv_id)
        
        # Normalize to text list
        if chunks and isinstance(chunks[0], Document):
            texts = [chunk.page_content for chunk in chunks]
        else:
            texts = chunks  # type: ignore
        
        # Generate embeddings
        vectors = await embed_texts(texts, self.embeddings_model)
        
        # Create database records
        cv_embeddings = []
        for i, (text, vector) in enumerate(zip(texts, vectors)):
            cv_embedding = CVEmbedding(
                cv_id=cv_id,
                chunk_text=text,
                chunk_index=i,
                embedding=vector,
                model=self.settings.embedding_model,
            )
            self.session.add(cv_embedding)
            cv_embeddings.append(cv_embedding)
        
        await self.session.flush()
        return cv_embeddings
    
    async def delete_cv_embeddings(self, cv_id: uuid.UUID) -> int:
        """
        Delete all embeddings for a CV.
        
        Args:
            cv_id: UUID of the CV.
        
        Returns:
            Number of embeddings deleted.
        """
        result = await self.session.execute(
            delete(CVEmbedding).where(CVEmbedding.cv_id == cv_id)
        )
        return result.rowcount  # type: ignore
    
    async def search_similar(
        self,
        cv_id: uuid.UUID,
        query: str,
        limit: int = 5,
    ) -> list[CVEmbedding]:
        """
        Search for CV chunks similar to a query.
        
        Uses cosine distance for similarity matching.
        
        Args:
            cv_id: UUID of the CV to search within.
            query: Search query text.
            limit: Maximum number of results.
        
        Returns:
            List of CVEmbedding objects ordered by similarity.
        
        Example:
            ```python
            results = await service.search_similar(
                cv_id=cv.id,
                query="What is their fintech experience?",
                limit=5
            )
            
            for embedding in results:
                print(f"Relevant chunk: {embedding.chunk_text[:100]}...")
            ```
        """
        # Generate embedding for the query
        query_embedding = await embed_text(query, self.embeddings_model)
        
        # Search using cosine distance
        result = await self.session.execute(
            select(CVEmbedding)
            .where(CVEmbedding.cv_id == cv_id)
            .order_by(CVEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        return list(result.scalars().all())
    
    async def search_all_cvs(
        self,
        query: str,
        limit: int = 10,
        user_id: uuid.UUID | None = None,
    ) -> list[CVEmbedding]:
        """
        Search across all CVs for similar content.
        
        Useful for finding candidates matching specific criteria.
        
        Args:
            query: Search query text.
            limit: Maximum number of results.
            user_id: Optional user ID to filter CVs (if multi-tenant).
        
        Returns:
            List of CVEmbedding objects from different CVs.
        
        Example:
            ```python
            results = await service.search_all_cvs(
                query="5+ years React experience in fintech",
                limit=10
            )
            
            # Group by CV
            cv_results = {}
            for embedding in results:
                if embedding.cv_id not in cv_results:
                    cv_results[embedding.cv_id] = []
                cv_results[embedding.cv_id].append(embedding)
            ```
        """
        query_embedding = await embed_text(query, self.embeddings_model)
        
        stmt = (
            select(CVEmbedding)
            .order_by(CVEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        # TODO: Add user_id filter when CV model has user_id relationship
        # if user_id:
        #     stmt = stmt.join(CV).where(CV.user_id == user_id)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_cv_embeddings(self, cv_id: uuid.UUID) -> list[CVEmbedding]:
        """
        Get all embeddings for a CV, ordered by chunk index.
        
        Args:
            cv_id: UUID of the CV.
        
        Returns:
            List of CVEmbedding objects.
        """
        result = await self.session.execute(
            select(CVEmbedding)
            .where(CVEmbedding.cv_id == cv_id)
            .order_by(CVEmbedding.chunk_index)
        )
        return list(result.scalars().all())
