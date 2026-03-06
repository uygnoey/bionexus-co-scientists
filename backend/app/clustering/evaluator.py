"""Cluster quality evaluation."""
from typing import List
import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score

from app.core.logging import get_logger
from app.models.hypothesis import HypothesisCluster

logger = get_logger(__name__)


class ClusterEvaluator:
    """Evaluate clustering quality."""

    @staticmethod
    def evaluate(
        embeddings: np.ndarray,
        labels: np.ndarray,
    ) -> dict:
        """Evaluate cluster quality.
        
        Args:
            embeddings: Embedding vectors
            labels: Cluster labels
            
        Returns:
            Dict with evaluation metrics
        """
        n_clusters = len(np.unique(labels))
        
        if n_clusters < 2:
            logger.warning("Cannot evaluate clustering with < 2 clusters")
            return {
                "silhouette_score": 0.0,
                "davies_bouldin_score": 0.0,
                "n_clusters": n_clusters,
            }
        
        silhouette = silhouette_score(embeddings, labels)
        davies_bouldin = davies_bouldin_score(embeddings, labels)
        
        logger.info(
            f"Cluster evaluation: silhouette={silhouette:.3f}, "
            f"davies_bouldin={davies_bouldin:.3f}"
        )
        
        return {
            "silhouette_score": float(silhouette),
            "davies_bouldin_score": float(davies_bouldin),
            "n_clusters": int(n_clusters),
        }

    @staticmethod
    def evaluate_clusters(clusters: List[HypothesisCluster]) -> dict:
        """Evaluate HypothesisCluster objects.
        
        Args:
            clusters: List of clusters
            
        Returns:
            Dict with cluster statistics
        """
        if not clusters:
            return {
                "n_clusters": 0,
                "avg_size": 0.0,
                "avg_diversity": 0.0,
                "avg_score": 0.0,
            }
        
        sizes = [c.size for c in clusters]
        diversities = [c.diversity_score for c in clusters]
        scores = [c.average_score for c in clusters]
        
        return {
            "n_clusters": len(clusters),
            "avg_size": float(np.mean(sizes)),
            "min_size": int(np.min(sizes)),
            "max_size": int(np.max(sizes)),
            "avg_diversity": float(np.mean(diversities)),
            "avg_score": float(np.mean(scores)),
            "total_hypotheses": sum(sizes),
        }
