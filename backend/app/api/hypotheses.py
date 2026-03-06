"""Hypotheses API router."""
from fastapi import APIRouter, HTTPException
from typing import List

from app.core.logging import get_logger
from app.models.hypothesis import HypothesisGenerationRequest, HypothesisGenerationResponse
from app.arxiv.client import ArxivClient
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.rag.retrieval import HybridRetriever
from app.agents.orchestrator import AgentOrchestrator

logger = get_logger(__name__)
router = APIRouter()


@router.post("/generate", response_model=HypothesisGenerationResponse)
async def generate_hypotheses(
    request: HypothesisGenerationRequest,
) -> HypothesisGenerationResponse:
    """Generate hypotheses from papers.
    
    Args:
        request: Generation request with paper IDs
        
    Returns:
        HypothesisGenerationResponse with generated hypotheses
    """
    logger.info(f"Generating hypotheses for {len(request.paper_ids)} papers")
    
    try:
        # Step 1: Fetch papers
        arxiv_client = ArxivClient()
        papers = await arxiv_client.get_papers_by_ids(request.paper_ids)
        
        if not papers:
            raise HTTPException(status_code=404, detail="No papers found")
        
        # Step 2: RAG retrieval
        retriever = HybridRetriever()
        await retriever.initialize()
        
        # Use first paper's abstract as query
        query = papers[0].abstract
        rag_results = await retriever.retrieve(query, top_k=10)
        rag_context = "\n".join([
            f"{r['title']}: {r['abstract'][:200]}..."
            for r in rag_results["vector_results"]
        ])
        
        # Step 3: Generate hypotheses
        orchestrator = AgentOrchestrator()
        response = await orchestrator.generate_hypotheses(
            papers=papers,
            rag_context=rag_context,
            max_hypotheses=request.max_hypotheses,
        )
        
        await retriever.close()
        
        return response
    
    except Exception as e:
        logger.error(f"Error generating hypotheses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health() -> dict:
    """Health check for hypotheses service."""
    return {"status": "healthy", "service": "hypotheses"}
