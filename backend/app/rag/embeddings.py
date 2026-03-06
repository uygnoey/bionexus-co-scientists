"""Embedding generation using OpenAI API."""
from typing import List

import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using OpenAI API."""

    def __init__(
        self,
        model: str = settings.embedding_model,
        dimension: int = settings.embedding_dimension,
    ) -> None:
        """Initialize embedding generator.
        
        Args:
            model: OpenAI embedding model name
            dimension: Embedding dimension
        """
        self.model = model
        self.dimension = dimension
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        logger.debug("Generating embedding", text_length=len(text))
        
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            
            embedding = response.data[0].embedding
            
            logger.debug(f"Generated embedding with dimension {len(embedding)}")
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts per batch
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts", batch_size=batch_size)
        
        all_embeddings: List[List[float]] = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(f"Processed batch {i // batch_size + 1}/{(len(texts) - 1) // batch_size + 1}")
            
            except Exception as e:
                logger.error(f"Error in batch {i // batch_size + 1}: {e}")
                raise
        
        logger.info(f"Generated {len(all_embeddings)} embeddings")
        return all_embeddings
