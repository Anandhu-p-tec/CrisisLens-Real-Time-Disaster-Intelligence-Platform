from __future__ import annotations

import json
import logging
from pathlib import Path
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

_logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'


class RAGRetriever:
    def __init__(self) -> None:
        self._encoder: SentenceTransformer | None = None
        self._index: faiss.IndexFlatL2 | None = None
        self._texts: list[str] = []
        self._post_ids: list[str] = []
        index_path = Path(settings.FAISS_INDEX_PATH)
        meta_path = index_path.with_suffix(".meta.json")
        if index_path.exists() and meta_path.exists():
            self._index = faiss.read_index(str(index_path))
            with meta_path.open() as f:
                meta = json.load(f)
            self._texts = meta["texts"]
            self._post_ids = meta["post_ids"]
            _logger.info("FAISS index loaded: %d vectors", self._index.ntotal)

    def _ensure_encoder(self) -> SentenceTransformer:
        if self._encoder is None:
            _logger.info("Lazy-loading SentenceTransformer...")
            self._encoder = SentenceTransformer(EMBEDDING_MODEL)
            if self._index is None:
                dim = self._encoder.get_sentence_embedding_dimension()
                self._index = faiss.IndexFlatL2(dim)
                _logger.info("FAISS index created fresh (dim=%d)", dim)
        return self._encoder

    def add(self, post_id: str, text: str) -> None:
        encoder = self._ensure_encoder()
        embedding: np.ndarray = encoder.encode([text], convert_to_numpy=True)
        self._index.add(embedding)  # type: ignore[union-attr]
        self._texts.append(text)
        self._post_ids.append(post_id)

    def retrieve(self, text: str, k: int = 3) -> list[str]:
        if self._index is None or self._index.ntotal == 0:
            return []
        encoder = self._ensure_encoder()
        embedding: np.ndarray = encoder.encode([text], convert_to_numpy=True)
        actual_k = min(k, self._index.ntotal)
        _, indices = self._index.search(embedding, actual_k)
        return [self._texts[i] for i in indices[0] if i < len(self._texts)]

    def persist(self) -> None:
        index_path = Path(settings.FAISS_INDEX_PATH)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(index_path))  # type: ignore[union-attr]
        meta_path = index_path.with_suffix(".meta.json")
        with meta_path.open("w") as f:
            json.dump({"texts": self._texts, "post_ids": self._post_ids}, f)
        _logger.info("FAISS index persisted: %d vectors", self._index.ntotal)  # type: ignore[union-attr]
