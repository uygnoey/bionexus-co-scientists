"""Unit tests for arXiv module."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.arxiv.client import ArxivClient
from app.models.paper import Paper


@pytest.fixture
def mock_arxiv_result():
    """Create mock arxiv.Result object."""
    result = MagicMock()
    result.entry_id = "http://arxiv.org/abs/2301.12345v1"
    result.title = "Test Paper Title"
    result.authors = [MagicMock(name="Alice Smith"), MagicMock(name="Bob Johnson")]
    result.summary = "This is a test abstract."
    result.published = datetime(2023, 1, 15)
    result.updated = datetime(2023, 1, 15)
    result.categories = ["cs.AI", "cs.LG"]
    result.pdf_url = "https://arxiv.org/pdf/2301.12345.pdf"
    return result


@pytest.mark.asyncio
async def test_search_papers(mock_arxiv_result):
    """Test paper search functionality."""
    client = ArxivClient(max_results=5)
    
    with patch.object(client.client, 'results', return_value=[mock_arxiv_result]):
        papers = await client.search_papers("quantum computing", max_results=1)
        
        assert len(papers) == 1
        assert papers[0].arxiv_id == "2301.12345"
        assert papers[0].title == "Test Paper Title"
        assert len(papers[0].authors) == 2
        assert papers[0].authors[0] == "Alice Smith"


@pytest.mark.asyncio
async def test_get_paper_by_id(mock_arxiv_result):
    """Test fetching paper by ID."""
    client = ArxivClient()
    
    with patch.object(client.client, 'results', return_value=[mock_arxiv_result]):
        paper = await client.get_paper_by_id("2301.12345")
        
        assert paper is not None
        assert paper.arxiv_id == "2301.12345"
        assert paper.title == "Test Paper Title"


@pytest.mark.asyncio
async def test_get_paper_by_id_not_found():
    """Test fetching non-existent paper."""
    client = ArxivClient()
    
    with patch.object(client.client, 'results', return_value=[]):
        paper = await client.get_paper_by_id("9999.99999")
        
        assert paper is None


@pytest.mark.asyncio
async def test_get_papers_by_ids(mock_arxiv_result):
    """Test fetching multiple papers by IDs."""
    client = ArxivClient()
    
    with patch.object(client.client, 'results', return_value=[mock_arxiv_result]):
        papers = await client.get_papers_by_ids(["2301.12345", "2302.67890"])
        
        assert len(papers) == 1
        assert papers[0].arxiv_id == "2301.12345"


def test_convert_to_paper(mock_arxiv_result):
    """Test arxiv.Result to Paper conversion."""
    client = ArxivClient()
    paper = client._convert_to_paper(mock_arxiv_result)
    
    assert isinstance(paper, Paper)
    assert paper.arxiv_id == "2301.12345"
    assert paper.title == "Test Paper Title"
    assert paper.authors == ["Alice Smith", "Bob Johnson"]
    assert paper.abstract == "This is a test abstract."
    assert paper.categories == ["cs.AI", "cs.LG"]
