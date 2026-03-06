"""PDF parser for extracting text and sections from arXiv papers."""
import re
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
import pdfplumber

from app.core.logging import get_logger
from app.models.paper import PaperSection

logger = get_logger(__name__)


class PaperParser:
    """Parser for extracting structured content from PDF papers."""

    # Common section headers (case-insensitive patterns)
    SECTION_PATTERNS = [
        r"^\s*abstract\s*$",
        r"^\s*\d+\.?\s+introduction\s*$",
        r"^\s*\d+\.?\s+related work\s*$",
        r"^\s*\d+\.?\s+background\s*$",
        r"^\s*\d+\.?\s+method(s|ology)?\s*$",
        r"^\s*\d+\.?\s+experiment(s|al results?)?\s*$",
        r"^\s*\d+\.?\s+results?\s*$",
        r"^\s*\d+\.?\s+discussion\s*$",
        r"^\s*\d+\.?\s+conclusion(s)?\s*$",
        r"^\s*\d+\.?\s+future work\s*$",
        r"^\s*references\s*$",
        r"^\s*appendix\s*$",
    ]

    def __init__(self) -> None:
        """Initialize parser."""
        self.section_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.SECTION_PATTERNS]

    async def parse_pdf(self, pdf_path: Path) -> Tuple[str, List[PaperSection]]:
        """Parse PDF and extract full text and sections.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (full_text, sections)
        """
        logger.info("Parsing PDF", path=str(pdf_path))
        
        # Extract full text using PyMuPDF (faster)
        full_text = await self._extract_text_pymupdf(pdf_path)
        
        # Extract sections using pdfplumber (better layout detection)
        sections = await self._extract_sections_pdfplumber(pdf_path)
        
        logger.info(
            "PDF parsed",
            path=str(pdf_path),
            text_length=len(full_text),
            sections=len(sections),
        )
        
        return full_text, sections

    async def _extract_text_pymupdf(self, pdf_path: Path) -> str:
        """Extract raw text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Full text content
        """
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_parts.append(text)
            
            doc.close()
            
            full_text = "\n\n".join(text_parts)
            return self._clean_text(full_text)
        
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {e}", path=str(pdf_path))
            return ""

    async def _extract_sections_pdfplumber(self, pdf_path: Path) -> List[PaperSection]:
        """Extract sections from PDF using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PaperSection objects
        """
        sections: List[PaperSection] = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                all_text = ""
                page_boundaries = []  # Track page numbers for sections
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    page_boundaries.append((len(all_text), page_num))
                    all_text += text + "\n\n"
                
                # Detect section headers
                section_starts = []
                lines = all_text.split("\n")
                current_pos = 0
                
                for line in lines:
                    line_stripped = line.strip()
                    if self._is_section_header(line_stripped):
                        section_starts.append((current_pos, line_stripped))
                    current_pos += len(line) + 1  # +1 for newline
                
                # Build sections
                for i, (start_pos, title) in enumerate(section_starts):
                    # Determine end position
                    end_pos = section_starts[i + 1][0] if i + 1 < len(section_starts) else len(all_text)
                    
                    content = all_text[start_pos:end_pos].strip()
                    
                    # Find page numbers
                    page_start = self._find_page_number(start_pos, page_boundaries)
                    page_end = self._find_page_number(end_pos, page_boundaries)
                    
                    section = PaperSection(
                        title=title,
                        content=self._clean_text(content),
                        page_start=page_start,
                        page_end=page_end,
                    )
                    sections.append(section)
        
        except Exception as e:
            logger.error(f"Error extracting sections with pdfplumber: {e}", path=str(pdf_path))
        
        return sections

    def _is_section_header(self, text: str) -> bool:
        """Check if text matches a section header pattern.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is a section header
        """
        for pattern in self.section_regex:
            if pattern.match(text):
                return True
        return False

    def _find_page_number(self, position: int, page_boundaries: List[Tuple[int, int]]) -> Optional[int]:
        """Find page number for a given text position.
        
        Args:
            position: Character position in full text
            page_boundaries: List of (position, page_number) tuples
            
        Returns:
            Page number or None
        """
        for boundary_pos, page_num in page_boundaries:
            if position < boundary_pos:
                return max(1, page_num - 1)
        return page_boundaries[-1][1] if page_boundaries else None

    def _clean_text(self, text: str) -> str:
        """Clean extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        
        # Remove hyphenation at line breaks
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        
        # Fix common encoding issues
        text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
        
        return text.strip()

    async def extract_abstract(self, pdf_path: Path) -> Optional[str]:
        """Extract only the abstract from a PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Abstract text or None
        """
        _, sections = await self.parse_pdf(pdf_path)
        
        for section in sections:
            if "abstract" in section.title.lower():
                return section.content
        
        return None


# Example usage
async def example_usage() -> None:
    """Example usage of PaperParser."""
    parser = PaperParser()
    
    pdf_path = Path("example_paper.pdf")
    if pdf_path.exists():
        full_text, sections = await parser.parse_pdf(pdf_path)
        
        print(f"Full text length: {len(full_text)} characters")
        print(f"Sections found: {len(sections)}")
        
        for section in sections[:5]:  # Print first 5 sections
            print(f"\n{section.title} (pages {section.page_start}-{section.page_end})")
            print(f"Content preview: {section.content[:200]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
