"""Hybrid retrieval combining vector and graph RAG."""
from typing import List, Dict, Any

from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.rag.graph_rag import GraphRAG
from app.core.logging import get_logger

logger = get_logger(__name__)


class HybridRetriever:
    """Hybrid retriever combining vector and graph RAG."""

    def __init__(self) -> None:
        """Initialize retriever."""
        self.embedding_gen = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.graph_rag = GraphRAG()

    async def initialize(self) -> None:
        """Initialize vector store."""
        await self.vector_store.initialize()

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        use_graph: bool = True,
    ) -> Dict[str, Any]:
        """Retrieve relevant context for query.
        
        Args:
            query: Query text
            top_k: Number of results
            use_graph: Whether to use graph RAG
            
        Returns:
            Dict with vector and graph results
        """
        logger.info("Retrieving context", query_length=len(query), use_graph=use_graph)
        
        # Vector search
        query_embedding = await self.embedding_gen.generate_embedding(query)
        vector_results = await self.vector_store.search(
            query_embedding=query_embedding,
            limit=top_k,
        )
        
        # Graph search (if enabled)
        graph_context = ""
        if use_graph and vector_results:
            # Extract entities from top results
            entity_names = []
            for result in vector_results[:3]:
                # Simple entity extraction from title
                words = result["title"].split()
                entity_names.extend(words[:5])
            
            graph_context = await self.graph_rag.query_context(entity_names)
        
        return {
            "vector_results": vector_results,
            "graph_context": graph_context,
            "query": query,
        }

    async def close(self) -> None:
        """Close connections."""
        await self.graph_rag.close()
