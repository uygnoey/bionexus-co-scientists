"""Unit tests for clustering module."""
import pytest
import numpy as np
from datetime import datetime

from app.clustering.kmeans import HypothesisClusterer
from app.clustering.evaluator import ClusterEvaluator
from app.models.hypothesis import Hypothesis, HypothesisScore


@pytest.fixture
def sample_hypotheses():
    """Create sample hypotheses for testing."""
    hypotheses = []
    for i in range(10):
        score = HypothesisScore(
            novelty=70.0 + i,
            feasibility=65.0 + i,
            impact=75.0 + i,
            overall=70.0 + i,
        )
        
        hyp = Hypothesis(
            id=f"hyp_{i}",
            text=f"Hypothesis {i}: Test hypothesis about topic {i % 3}",
            description=f"Description for hypothesis {i}",
            score=score,
            source_papers=[f"paper_{i}"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        hypotheses.append(hyp)
    
    return hypotheses


@pytest.mark.asyncio
async def test_cluster_basic(sample_hypotheses):
    """Test basic clustering functionality."""
    clusterer = HypothesisClusterer()
    clusters = await clusterer.cluster(sample_hypotheses, n_clusters=3)
    
    assert len(clusters) == 3
    assert all(isinstance(c.cluster_id, int) for c in clusters)
    assert sum(c.size for c in clusters) == len(sample_hypotheses)


@pytest.mark.asyncio
async def test_cluster_too_few_hypotheses():
    """Test clustering with too few hypotheses."""
    clusterer = HypothesisClusterer()
    
    score = HypothesisScore(novelty=70.0, feasibility=65.0, impact=75.0, overall=70.0)
    hyp = Hypothesis(
        id="hyp_1",
        text="Single hypothesis",
        description="Test",
        score=score,
        source_papers=["paper_1"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    clusters = await clusterer.cluster([hyp])
    
    assert len(clusters) == 1
    assert clusters[0].size == 1


def test_cluster_evaluator_basic():
    """Test cluster evaluator with basic inputs."""
    embeddings = np.random.rand(20, 128)
    labels = np.array([0] * 10 + [1] * 10)
    
    results = ClusterEvaluator.evaluate(embeddings, labels)
    
    assert "silhouette_score" in results
    assert "davies_bouldin_score" in results
    assert results["n_clusters"] == 2
    assert -1.0 <= results["silhouette_score"] <= 1.0


def test_cluster_evaluator_single_cluster():
    """Test evaluator with single cluster."""
    embeddings = np.random.rand(10, 128)
    labels = np.zeros(10, dtype=int)
    
    results = ClusterEvaluator.evaluate(embeddings, labels)
    
    assert results["n_clusters"] == 1
    assert results["silhouette_score"] == 0.0
