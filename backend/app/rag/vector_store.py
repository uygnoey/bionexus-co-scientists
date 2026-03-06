"""Qdrant vector store for semantic search."""
from typing import Dict, List, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.core.config import settings
from app.core.logging import get_logger
from app.models.paper import Paper

logger = get_logger(__name__)


class VectorStore:
    """Qdrant vector store for papers."""

    COLLECTION_NAME = "papers"

    def __init__(self) -> None:
        """Initialize Qdrant client."""
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

    async def initialize(self) -> None:
        """Create collection if it doesn't exist."""
        collections = await self.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if self.COLLECTION_NAME not in collection_names:
            logger.info(f"Creating collection: {self.COLLECTION_NAME}")
            
            await self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )
            
            logger.info(f"Collection created: {self.COLLECTION_NAME}")
        else:
            logger.info(f"Collection already exists: {self.COLLECTION_NAME}")

    async def upsert_paper(
        self, paper: Paper, embedding: List[float], chunk_index: int = 0
    ) -> str:
        """Insert or update a paper embedding.
        
        Args:
            paper: Paper object
            embedding: Embedding vector
            chunk_index: Chunk index if paper is split
            
        Returns:
            Point ID
        """
        point_id = f"{paper.arxiv_id}_chunk_{chunk_index}"
        
        payload = {
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "abstract": paper.abstract,
            "authors": paper.authors,
            "published_date": paper.published_date.isoformat(),
            "categories": paper.categories,
            "chunk_index": chunk_index,
        }
        
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload=payload,
        )
        
        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
        )
        
        logger.debug(f"Upserted paper: {point_id}")
        return point_id

    async def upsert_papers_batch(
        self, papers: List[Paper], embeddings: List[List[float]]
    ) -> List[str]:
        """Insert or update multiple papers.
        
        Args:
            papers: List of Paper objects
            embeddings: List of embedding vectors
            
        Returns:
            List of point IDs
        """
        if len(papers) != len(embeddings):
            raise ValueError("Number of papers must match number of embeddings")
        
        points = []
        point_ids = []
        
        for paper, embedding in zip(papers, embeddings):
            point_id = f"{paper.arxiv_id}_chunk_0"
            point_ids.append(point_id)
            
            payload = {
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "published_date": paper.published_date.isoformat(),
                "categories": paper.categories,
                "chunk_index": 0,
            }
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )
        
        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )
        
        logger.info(f"Upserted {len(points)} papers")
        return point_ids

    async def search(
        self,
        query_embedding: List[float],
        limit: int = settings.rag_top_k,
        score_threshold: Optional[float] = settings.rag_score_threshold,
        filter_categories: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Search for similar papers.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
            score_threshold: Minimum similarity score
            filter_categories: Filter by arXiv categories
            
        Returns:
            List of search results with scores
        """
        query_filter = None
        if filter_categories:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="categories",
                        match=MatchValue(any=filter_categories),
                    )
                ]
            )
        
        results = await self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        
        search_results = [
            {
                "arxiv_id": hit.payload["arxiv_id"],
                "title": hit.payload["title"],
                "abstract": hit.payload["abstract"],
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results
        ]
        
        logger.info(f"Found {len(search_results)} results")
        return search_results

    async def delete_paper(self, arxiv_id: str) -> None:
        """Delete all chunks of a paper.
        
        Args:
            arxiv_id: arXiv ID
        """
        await self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="arxiv_id",
                        match=MatchValue(value=arxiv_id),
                    )
                ]
            ),
        )
        
        logger.info(f"Deleted paper: {arxiv_id}")

    async def count(self) -> int:
        """Count total points in collection.
        
        Returns:
            Number of points
        """
        info = await self.client.get_collection(self.COLLECTION_NAME)
        return info.points_count
