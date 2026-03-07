"""Papers API router."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.core.logging import get_logger
from app.core.cache import cache, cache_key
from app.models.paper import Paper
from app.arxiv.client import ArxivClient

logger = get_logger(__name__)
router = APIRouter()


@router.get("/search", response_model=List[Paper])
async def search_papers(
    query: str = Query(..., min_length=1, description="Search query"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum results"),
) -> List[Paper]:
    """Search arXiv papers.
    
    Args:
        query: Search query
        max_results: Maximum results
        
    Returns:
        List of papers
    """
    logger.info(f"Searching papers: {query}")
    
    # Check cache first
    cache_k = cache_key("papers", "search", query, str(max_results))
    cached = await cache.get(cache_k)
    if cached:
        logger.info(f"Cache hit for papers search: {query}")
        return [Paper(**p) for p in cached]
    
    try:
        client = ArxivClient(max_results=max_results)
        papers = await client.search_papers(query, max_results=max_results)
        
        # Cache results (1 hour)
        await cache.set(cache_k, [p.model_dump() for p in papers], ttl=3600)
        
        return papers
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{arxiv_id}", response_model=Paper)
async def get_paper(arxiv_id: str) -> Paper:
    """Get paper by arXiv ID.
    
    Args:
        arxiv_id: arXiv ID
        
    Returns:
        Paper object
    """
    logger.info(f"Fetching paper: {arxiv_id}")
    
    try:
        client = ArxivClient()
        paper = await client.get_paper_by_id(arxiv_id)
        
        if not paper:
            raise HTTPException(status_code=404, detail=f"Paper {arxiv_id} not found")
        
        return paper
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health() -> dict:
    """Health check for papers service."""
    return {"status": "healthy", "service": "papers"}
