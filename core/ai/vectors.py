from __future__ import annotations

from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from core.config import settings

# Размерность вектора для модели all-MiniLM-L6-v2
_DEFAULT_EMBEDDING_DIM = 384


@lru_cache(maxsize=1)
def _get_model():
    """
    Загружает модель один раз при первом вызове и сохраняет её в кэше.
    """
    return SentenceTransformer(settings.ai_model_name)


def encode_titles(titles: List[str]):
    """
    Превращает список заголовков окон в таблицу чисел (матрицу эмбеддингов).

    ИИ переводит каждый заголовок в уникальный цифровой вектор фиксированной длины,
    который кодирует смысл текста. Похожие по контексту окна получают близкие координаты в пространстве. Это позволяет
    алгоритму K-Means легко объединять их в группы. Эмбеддинги нормализуются по L2, чтобы евклидово расстояние
    между ними было согласовано с косинусной близостью.
    """
    if not titles:
        return np.empty((0, _DEFAULT_EMBEDDING_DIM))

    unique_titles = list(set(titles))

    model = _get_model()
    unique_embeddings = model.encode(
        unique_titles,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    title_to_vector = {title: vector for title, vector in zip(unique_titles, unique_embeddings)}

    full_embeddings = [title_to_vector[title] for title in titles]

    return np.asarray(full_embeddings)