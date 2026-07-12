from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
from sklearn.cluster import KMeans

from core.config import settings


@dataclass(frozen=True)
class ClusterSummary:
    cluster_id: int
    size: int
    top_titles: List[str]


class ClusterBrain:
    """
    Группировка заголовков окон по темам на основе алгоритма K-Means.
    """

    def __init__(self, n_clusters: Optional[int] = None):
        self.n_clusters: int = n_clusters or settings.ai_n_clusters
        self._model: Optional[KMeans] = None
        self._labels: Optional[np.ndarray] = None

    def fit(self, embeddings: np.ndarray):
        """
        Обучает K-Means на матрице эмбеддингов и возвращает номер кластера для каждого заголовка.

        Алгоритм ищет центроиды групп и объединяет вокруг них ближайшие векторы,
        пока они не распределятся максимально кучно.
        """
        n_samples = embeddings.shape[0]
        effective_k = max(1, min(self.n_clusters, n_samples))

        self._model = KMeans(
            n_clusters=effective_k,
            random_state=42,
            n_init="auto"
        )
        self._labels = self._model.fit_predict(embeddings)
        return self._labels

    def summarize(self, titles: List[str], embeddings: np.ndarray, top_n: Optional[int] = None):
        """
        Для каждого кластера находит top_n заголовков, ближайших к его
        центроиду по евклидову расстоянию.
        """
        if self._model is None or self._labels is None:
            raise RuntimeError("Сначала вызовите fit()")

        top_n = top_n or settings.ai_top_n_titles
        centroids = self._model.cluster_centers_

        clusters_to_indices: Dict[int, List[int]] = defaultdict(list)
        for idx, label in enumerate(self._labels):
            clusters_to_indices[int(label)].append(idx)

        summaries: List[ClusterSummary] = []
        for cluster_id, indices in sorted(clusters_to_indices.items()):
            cluster_vectors = embeddings[indices]
            centroid = centroids[cluster_id]

            # Евклидово расстояние каждой точки кластера до его центроида
            distances = np.linalg.norm(cluster_vectors - centroid, axis=1)
            closest_order = np.argsort(distances)

            top_titles: List[str] = []
            seen_titles: set = set()
            for pos in closest_order:
                title = titles[indices[pos]]
                if title not in seen_titles:
                    seen_titles.add(title)
                    top_titles.append(title)
                if len(top_titles) >= top_n:
                    break

            summaries.append(
                ClusterSummary(
                    cluster_id=cluster_id,
                    size=len(indices),
                    top_titles=top_titles,
                )
            )

        return summaries