"""PDF downloader for arXiv papers."""
import asyncio
from pathlib import Path
from typing import List, Optional

import aiofiles
import httpx

from app.core.logging import get_logger
from app.models.paper import Paper

logger = get_logger(__name__)


class ArxivDownloader:
    """Downloader for arXiv PDF files."""

    def __init__(self, download_dir: Path, timeout: int = 60) -> None:
        """Initialize downloader.
        
        Args:
            download_dir: Directory to save PDFs
            timeout: Download timeout in seconds
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout

    async def download_paper(self, paper: Paper, overwrite: bool = False) -> Optional[Path]:
        """Download PDF for a single paper.
        
        Args:
            paper: Paper object with PDF URL
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to downloaded PDF, or None if failed
        """
        pdf_path = self.download_dir / f"{paper.arxiv_id}.pdf"
        
        if pdf_path.exists() and not overwrite:
            logger.info(f"PDF already exists, skipping download", arxiv_id=paper.arxiv_id)
            return pdf_path
        
        logger.info("Downloading PDF", arxiv_id=paper.arxiv_id, url=str(paper.pdf_url))
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(str(paper.pdf_url), follow_redirects=True)
                response.raise_for_status()
                
                async with aiofiles.open(pdf_path, "wb") as f:
                    await f.write(response.content)
            
            file_size = pdf_path.stat().st_size
            logger.info(
                "PDF downloaded",
                arxiv_id=paper.arxiv_id,
                path=str(pdf_path),
                size_mb=round(file_size / 1024 / 1024, 2),
            )
            
            return pdf_path
        
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error downloading PDF: {e.response.status_code}",
                arxiv_id=paper.arxiv_id,
                url=str(paper.pdf_url),
            )
            return None
        
        except httpx.TimeoutException:
            logger.error(
                "Timeout downloading PDF",
                arxiv_id=paper.arxiv_id,
                timeout=self.timeout,
            )
            return None
        
        except Exception as e:
            logger.error(
                f"Error downloading PDF: {e}",
                arxiv_id=paper.arxiv_id,
                url=str(paper.pdf_url),
            )
            return None

    async def download_papers(
        self,
        papers: List[Paper],
        max_concurrent: int = 5,
        overwrite: bool = False,
    ) -> List[Optional[Path]]:
        """Download PDFs for multiple papers concurrently.
        
        Args:
            papers: List of Paper objects
            max_concurrent: Maximum concurrent downloads
            overwrite: Whether to overwrite existing files
            
        Returns:
            List of paths (None for failed downloads)
        """
        logger.info(f"Downloading {len(papers)} papers", max_concurrent=max_concurrent)
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(paper: Paper) -> Optional[Path]:
            async with semaphore:
                return await self.download_paper(paper, overwrite=overwrite)
        
        tasks = [download_with_semaphore(paper) for paper in papers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to None
        paths = [
            result if not isinstance(result, Exception) else None
            for result in results
        ]
        
        successful = sum(1 for path in paths if path is not None)
        logger.info(f"Downloaded {successful}/{len(papers)} papers successfully")
        
        return paths

    async def download_by_id(
        self, arxiv_id: str, pdf_url: Optional[str] = None, overwrite: bool = False
    ) -> Optional[Path]:
        """Download PDF by arXiv ID.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2301.12345")
            pdf_url: PDF URL (if known, otherwise constructed)
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to downloaded PDF, or None if failed
        """
        # Clean ID
        clean_id = arxiv_id.replace("arXiv:", "").strip()
        
        # Construct PDF URL if not provided
        if pdf_url is None:
            pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
        
        # Create minimal Paper object
        from pydantic import HttpUrl
        from datetime import datetime
        
        paper = Paper(
            arxiv_id=clean_id,
            title="",
            authors=[],
            abstract="",
            published_date=datetime.now(),
            pdf_url=HttpUrl(pdf_url),
        )
        
        return await self.download_paper(paper, overwrite=overwrite)

    def get_pdf_path(self, arxiv_id: str) -> Path:
        """Get path where PDF would be stored.
        
        Args:
            arxiv_id: arXiv ID
            
        Returns:
            Path to PDF file
        """
        clean_id = arxiv_id.replace("arXiv:", "").strip()
        return self.download_dir / f"{clean_id}.pdf"

    def is_downloaded(self, arxiv_id: str) -> bool:
        """Check if paper is already downloaded.
        
        Args:
            arxiv_id: arXiv ID
            
        Returns:
            True if PDF exists
        """
        return self.get_pdf_path(arxiv_id).exists()

    def cleanup_old_pdfs(self, keep_days: int = 30) -> int:
        """Remove PDFs older than specified days.
        
        Args:
            keep_days: Number of days to keep PDFs
            
        Returns:
            Number of files removed
        """
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (keep_days * 24 * 60 * 60)
        
        removed = 0
        for pdf_path in self.download_dir.glob("*.pdf"):
            if pdf_path.stat().st_mtime < cutoff_time:
                pdf_path.unlink()
                removed += 1
                logger.info("Removed old PDF", path=str(pdf_path))
        
        logger.info(f"Cleaned up {removed} old PDFs", keep_days=keep_days)
        return removed


# Example usage
async def example_usage() -> None:
    """Example usage of ArxivDownloader."""
    downloader = ArxivDownloader(download_dir=Path("./downloads"))
    
    # Download single paper by ID
    pdf_path = await downloader.download_by_id("2301.12345")
    if pdf_path:
        print(f"Downloaded to: {pdf_path}")
    
    # Check if downloaded
    if downloader.is_downloaded("2301.12345"):
        print("Paper is already downloaded")
    
    # Cleanup old files
    removed = downloader.cleanup_old_pdfs(keep_days=7)
    print(f"Removed {removed} old PDFs")


if __name__ == "__main__":
    asyncio.run(example_usage())
