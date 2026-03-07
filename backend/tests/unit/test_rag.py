"""Unit tests for RAG modules."""
import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

from app.rag.embeddings import EmbeddingGenerator


@pytest.mark.asyncio
async def test_embedding_generator_single():
    """Test single embedding generation."""
    gen = EmbeddingGenerator()
    
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
    
    with patch.object(gen.client.embeddings, 'create', return_value=mock_response):
        embedding = await gen.generate_embedding("test text")
        
        assert len(embedding) == 1536
        assert isinstance(embedding, list)


@pytest.mark.asyncio
async def test_embedding_generator_batch():
    """Test batch embedding generation."""
    gen = EmbeddingGenerator()
    
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1] * 1536),
        MagicMock(embedding=[0.2] * 1536),
    ]
    
    with patch.object(gen.client.embeddings, 'create', return_value=mock_response):
        embeddings = await gen.generate_embeddings_batch(
            ["text1", "text2"],
            batch_size=2
        )
        
        assert len(embeddings) == 2
        assert all(len(e) == 1536 for e in embeddings)


def test_embedding_dimension():
    """Test embedding dimension configuration."""
    from app.core.config import settings
    
    gen = EmbeddingGenerator()
    assert gen.dimension == settings.embedding_dimension
