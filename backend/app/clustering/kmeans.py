"""KMeans clustering for hypotheses."""
from typing import List, Optional
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from app.core.config import settings
from app.core.logging import get_logger
from app.models.hypothesis import Hypothesis, HypothesisCluster
from app.rag.embeddings import EmbeddingGenerator

logger = get_logger(__name__)


class HypothesisClusterer:
    """Cluster hypotheses using KMeans."""

    def __init__(self) -> None:
        """Initialize clusterer."""
        self.embedding_gen = EmbeddingGenerator()
        self.min_clusters = settings.cluster_min
        self.max_clusters = settings.cluster_max

    async def cluster(
        self,
        hypotheses: List[Hypothesis],
        n_clusters: Optional[int] = None,
    ) -> List[HypothesisCluster]:
        """Cluster hypotheses.
        
        Args:
            hypotheses: List of hypotheses to cluster
            n_clusters: Number of clusters (auto-detected if None)
            
        Returns:
            List of HypothesisCluster objects
        """
        if len(hypotheses) < self.min_clusters:
            logger.info(f"Not enough hypotheses to cluster ({len(hypotheses)} < {self.min_clusters})")
            # Return single cluster with all hypotheses
            return [
                HypothesisCluster(
                    cluster_id=0,
                    hypotheses=[h.id for h in hypotheses],
                    centroid_text=hypotheses[0].text if hypotheses else "",
                    diversity_score=1.0,
                    size=len(hypotheses),
                    best_hypothesis_id=hypotheses[0].id if hypotheses else None,
                    average_score=np.mean([h.score.overall for h in hypotheses]),
                )
            ]
        
        logger.info(f"Clustering {len(hypotheses)} hypotheses")
        
        # Generate embeddings
        texts = [h.text for h in hypotheses]
        embeddings = await self.embedding_gen.generate_embeddings_batch(texts)
        embeddings_array = np.array(embeddings)
        
        # Determine optimal number of clusters
        if n_clusters is None:
            n_clusters = self._find_optimal_clusters(embeddings_array)
        
        n_clusters = max(self.min_clusters, min(n_clusters, len(hypotheses) // 2))
        
        logger.info(f"Using {n_clusters} clusters")
        
        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings_array)
        
        # Build clusters
        clusters: List[HypothesisCluster] = []
        
        for cluster_id in range(n_clusters):
            cluster_mask = labels == cluster_id
            cluster_hypotheses = [h for h, mask in zip(hypotheses, cluster_mask) if mask]
            
            if not cluster_hypotheses:
                continue
            
            # Find centroid (closest hypothesis to cluster center)
            cluster_embeddings = embeddings_array[cluster_mask]
            centroid = kmeans.cluster_centers_[cluster_id]
            distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
            centroid_idx = np.argmin(distances)
            centroid_text = cluster_hypotheses[centroid_idx].text
            
            # Calculate diversity (average pairwise distance)
            diversity = self._calculate_diversity(cluster_embeddings)
            
            # Find best hypothesis in cluster
            best_hypothesis = max(cluster_hypotheses, key=lambda h: h.score.overall)
            
            # Average score
            avg_score = np.mean([h.score.overall for h in cluster_hypotheses])
            
            cluster = HypothesisCluster(
                cluster_id=cluster_id,
                hypotheses=[h.id for h in cluster_hypotheses],
                centroid_text=centroid_text,
                diversity_score=float(diversity),
                size=len(cluster_hypotheses),
                best_hypothesis_id=best_hypothesis.id,
                average_score=float(avg_score),
            )
            clusters.append(cluster)
        
        # Update hypotheses with cluster IDs
        for cluster in clusters:
            for hyp_id in cluster.hypotheses:
                for hyp in hypotheses:
                    if hyp.id == hyp_id:
                        hyp.cluster_id = cluster.cluster_id
        
        logger.info(f"Created {len(clusters)} clusters")
        return clusters

    def _find_optimal_clusters(self, embeddings: np.ndarray) -> int:
        """Find optimal number of clusters using elbow method.
        
        Args:
            embeddings: Embedding vectors
            
        Returns:
            Optimal number of clusters
        """
        max_k = min(self.max_clusters, len(embeddings) // 2)
        
        if max_k < self.min_clusters:
            return self.min_clusters
        
        # Calculate silhouette scores for different k
        silhouette_scores = []
        k_range = range(self.min_clusters, max_k + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            silhouette_scores.append(score)
        
        # Find k with highest silhouette score
        best_k = k_range[np.argmax(silhouette_scores)]
        
        logger.info(f"Optimal clusters: {best_k} (silhouette: {max(silhouette_scores):.3f})")
        return best_k

    def _calculate_diversity(self, embeddings: np.ndarray) -> float:
        """Calculate diversity within cluster.
        
        Args:
            embeddings: Cluster embeddings
            
        Returns:
            Diversity score (0-1)
        """
        if len(embeddings) < 2:
            return 1.0
        
        # Average pairwise cosine distance
        from sklearn.metrics.pairwise import cosine_distances
        
        distances = cosine_distances(embeddings)
        # Get upper triangle (exclude diagonal)
        triu_indices = np.triu_indices_from(distances, k=1)
        pairwise_distances = distances[triu_indices]
        
        diversity = float(np.mean(pairwise_distances))
        return min(1.0, max(0.0, diversity))
