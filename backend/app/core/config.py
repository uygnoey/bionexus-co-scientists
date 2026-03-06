"""Configuration management using Pydantic Settings."""
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Anthropic API
    anthropic_api_key: str = Field(..., description="Anthropic API key")

    # OpenAI (for embeddings)
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="password", description="Neo4j password")

    # Qdrant
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API key")

    # Redis
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")

    # Application
    app_name: str = Field(default="BioNexus Co-scientists", description="App name")
    app_version: str = Field(default="0.1.0", description="App version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="API workers")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.strip("[]").split(",")]
        return v

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60, description="Rate limit per minute per IP"
    )

    # RAG Settings
    embedding_model: str = Field(
        default="text-embedding-3-small", description="OpenAI embedding model"
    )
    embedding_dimension: int = Field(
        default=1536, description="Embedding vector dimension"
    )
    rag_top_k: int = Field(default=10, description="Top-K results for RAG retrieval")
    rag_score_threshold: float = Field(
        default=0.7, description="Minimum similarity score for RAG"
    )

    # Graph RAG
    graph_max_entities: int = Field(
        default=100, description="Max entities to extract per paper"
    )
    graph_hop_limit: int = Field(default=2, description="Max hops for graph traversal")

    # Agent Settings
    generator_model: str = Field(
        default="claude-opus-4-6", description="Generator agent model"
    )
    validator_model: str = Field(
        default="claude-sonnet-4-5", description="Validator agent model"
    )
    ranker_model: str = Field(default="claude-haiku-4-6", description="Ranker agent model")
    debate_rounds: int = Field(default=3, description="Number of debate rounds")
    max_hypotheses: int = Field(default=5, description="Max hypotheses to generate")

    # Clustering
    cluster_method: str = Field(default="kmeans", description="Clustering method")
    cluster_min: int = Field(default=2, description="Min clusters")
    cluster_max: int = Field(default=5, description="Max clusters")

    @property
    def redis_url(self) -> str:
        """Generate Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def qdrant_url(self) -> str:
        """Generate Qdrant URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


# Global settings instance
settings = Settings()
