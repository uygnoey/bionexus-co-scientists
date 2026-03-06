"""Paper and entity data models."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class EntityType(str, Enum):
    """Entity types for knowledge graph."""

    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    CONCEPT = "CONCEPT"
    METHOD = "METHOD"
    DATASET = "DATASET"
    METRIC = "METRIC"


class Entity(BaseModel):
    """Entity extracted from papers."""

    id: str = Field(..., description="Unique entity ID")
    name: str = Field(..., description="Entity name")
    type: EntityType = Field(..., description="Entity type")
    mention_count: int = Field(default=1, description="Number of mentions")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    papers: List[str] = Field(default_factory=list, description="Paper IDs mentioning this entity")


class RelationType(str, Enum):
    """Relationship types between entities."""

    USES = "USES"
    RELATED_TO = "RELATED_TO"
    IS_A = "IS_A"
    EXTENDS = "EXTENDS"
    COMPARES_WITH = "COMPARES_WITH"
    PROPOSED_BY = "PROPOSED_BY"


class Relationship(BaseModel):
    """Relationship between two entities."""

    id: str = Field(..., description="Unique relationship ID")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    type: RelationType = Field(..., description="Relationship type")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    paper_id: str = Field(..., description="Paper ID where relationship was found")


class PaperSection(BaseModel):
    """Section of a paper."""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    page_start: Optional[int] = Field(None, description="Starting page number")
    page_end: Optional[int] = Field(None, description="Ending page number")


class Paper(BaseModel):
    """arXiv paper metadata and content."""

    arxiv_id: str = Field(..., description="arXiv ID (e.g., 2301.12345)")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of author names")
    abstract: str = Field(..., description="Paper abstract")
    published_date: datetime = Field(..., description="Publication date")
    updated_date: Optional[datetime] = Field(None, description="Last update date")
    categories: List[str] = Field(default_factory=list, description="arXiv categories")
    pdf_url: HttpUrl = Field(..., description="PDF download URL")
    
    # Optional processed content
    full_text: Optional[str] = Field(None, description="Full paper text (if parsed)")
    sections: List[PaperSection] = Field(default_factory=list, description="Paper sections")
    
    # Metadata
    citation_count: Optional[int] = Field(None, description="Number of citations")
    entities: List[str] = Field(default_factory=list, description="Extracted entity IDs")
    embedding_id: Optional[str] = Field(None, description="Qdrant vector ID")
    
    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "arxiv_id": "2301.12345",
                "title": "Advances in Quantum Computing",
                "authors": ["Alice Smith", "Bob Johnson"],
                "abstract": "We present novel approaches to quantum error correction...",
                "published_date": "2023-01-15T00:00:00Z",
                "categories": ["quant-ph", "cs.ET"],
                "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
            }
        }
