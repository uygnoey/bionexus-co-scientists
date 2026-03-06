"""arXiv API client for searching and fetching papers."""
import asyncio
from datetime import datetime
from typing import List, Optional

import arxiv
from pydantic import HttpUrl

from app.core.logging import get_logger
from app.models.paper import Paper

logger = get_logger(__name__)


class ArxivClient:
    """Client for interacting with arXiv API."""

    def __init__(self, max_results: int = 100) -> None:
        """Initialize arXiv client.
        
        Args:
            max_results: Maximum results per query
        """
        self.max_results = max_results
        self.client = arxiv.Client()

    async def search_papers(
        self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
        sort_order: arxiv.SortOrder = arxiv.SortOrder.Descending,
    ) -> List[Paper]:
        """Search arXiv for papers matching query.
        
        Args:
            query: Search query (keywords, authors, etc.)
            max_results: Maximum results to return (overrides default)
            sort_by: Sort criterion
            sort_order: Sort order
            
        Returns:
            List of Paper objects
        """
        logger.info("Searching arXiv", query=query, max_results=max_results or self.max_results)
        
        search = arxiv.Search(
            query=query,
            max_results=max_results or self.max_results,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Run search in thread pool (arxiv library is synchronous)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, lambda: list(self.client.results(search))
        )
        
        papers = [self._convert_to_paper(result) for result in results]
        
        logger.info(f"Found {len(papers)} papers", query=query)
        return papers

    async def get_paper_by_id(self, arxiv_id: str) -> Optional[Paper]:
        """Fetch a specific paper by arXiv ID.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2301.12345" or "arXiv:2301.12345")
            
        Returns:
            Paper object if found, None otherwise
        """
        # Clean ID (remove "arXiv:" prefix if present)
        clean_id = arxiv_id.replace("arXiv:", "").strip()
        
        logger.info("Fetching paper by ID", arxiv_id=clean_id)
        
        search = arxiv.Search(id_list=[clean_id])
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, lambda: list(self.client.results(search))
        )
        
        if not results:
            logger.warning("Paper not found", arxiv_id=clean_id)
            return None
        
        paper = self._convert_to_paper(results[0])
        logger.info("Paper found", arxiv_id=clean_id, title=paper.title)
        return paper

    async def get_papers_by_ids(self, arxiv_ids: List[str]) -> List[Paper]:
        """Fetch multiple papers by arXiv IDs.
        
        Args:
            arxiv_ids: List of arXiv IDs
            
        Returns:
            List of Paper objects (may be shorter if some IDs not found)
        """
        # Clean IDs
        clean_ids = [aid.replace("arXiv:", "").strip() for aid in arxiv_ids]
        
        logger.info("Fetching papers by IDs", count=len(clean_ids))
        
        search = arxiv.Search(id_list=clean_ids)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, lambda: list(self.client.results(search))
        )
        
        papers = [self._convert_to_paper(result) for result in results]
        
        logger.info(f"Found {len(papers)}/{len(clean_ids)} papers")
        return papers

    async def search_by_author(
        self, author: str, max_results: Optional[int] = None
    ) -> List[Paper]:
        """Search papers by author name.
        
        Args:
            author: Author name
            max_results: Maximum results
            
        Returns:
            List of Paper objects
        """
        query = f'au:"{author}"'
        return await self.search_papers(query, max_results=max_results)

    async def search_by_category(
        self, category: str, max_results: Optional[int] = None
    ) -> List[Paper]:
        """Search papers by arXiv category.
        
        Args:
            category: arXiv category (e.g., "cs.AI", "quant-ph")
            max_results: Maximum results
            
        Returns:
            List of Paper objects
        """
        query = f"cat:{category}"
        return await self.search_papers(
            query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
        )

    async def search_recent(
        self, category: Optional[str] = None, max_results: Optional[int] = None
    ) -> List[Paper]:
        """Search recent papers (last 7 days).
        
        Args:
            category: Optional arXiv category filter
            max_results: Maximum results
            
        Returns:
            List of Paper objects sorted by submission date
        """
        query = f"cat:{category}" if category else "all"
        
        return await self.search_papers(
            query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

    def _convert_to_paper(self, result: arxiv.Result) -> Paper:
        """Convert arxiv.Result to Paper model.
        
        Args:
            result: arxiv.Result object
            
        Returns:
            Paper object
        """
        # Extract arXiv ID (remove version if present)
        arxiv_id = result.entry_id.split("/")[-1].split("v")[0]
        
        # Convert authors
        authors = [author.name for author in result.authors]
        
        # Convert categories
        categories = result.categories
        
        # Published and updated dates
        published_date = result.published
        updated_date = result.updated if result.updated != result.published else None
        
        return Paper(
            arxiv_id=arxiv_id,
            title=result.title,
            authors=authors,
            abstract=result.summary,
            published_date=published_date,
            updated_date=updated_date,
            categories=categories,
            pdf_url=HttpUrl(result.pdf_url),
        )


# Example usage
async def example_usage() -> None:
    """Example usage of ArxivClient."""
    client = ArxivClient(max_results=5)
    
    # Search by keyword
    papers = await client.search_papers("quantum computing error correction")
    for paper in papers:
        print(f"{paper.arxiv_id}: {paper.title}")
    
    # Get specific paper
    paper = await client.get_paper_by_id("2301.12345")
    if paper:
        print(f"Found: {paper.title}")
    
    # Search recent papers in a category
    recent = await client.search_recent(category="quant-ph", max_results=10)
    print(f"Found {len(recent)} recent papers in quant-ph")


if __name__ == "__main__":
    asyncio.run(example_usage())
