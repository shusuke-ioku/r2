"""Sentence-transformers embedding wrapper."""

from __future__ import annotations

import logging
import os

import numpy as np

# Suppress noisy model loading progress bars
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info("Loading embedding model: %s", model_name)
        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of documents."""
        embeddings = self._model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        embedding = self._model.encode([query], show_progress_bar=False)
        return embedding[0].tolist()
