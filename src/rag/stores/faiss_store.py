"""
Backend FAISS -- index in-memory, baseline du benchmark.
Avantages : latence minimale. Limites : pas de persistance,
pas de filtrage metadonnees natif (filtrage manuel ci-dessous).
"""
import numpy as np
import faiss

from src.rag.config import cfg
from src.rag.ingestion.chunking import Chunk
from src.rag.stores.base import VectorStore


class FaissStore(VectorStore):
    def __init__(self):
        self._index = faiss.IndexFlatIP(cfg.embedding.dimension)
        self._chunks: list[Chunk] = []

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        vecs = np.array(vectors, dtype="float32")
        self._index.add(vecs)
        self._chunks.extend(chunks)
        print(f"[faiss] {len(chunks)} chunks ajoutes (total={len(self._chunks)})")

    def search(self, vector: list[float], k: int, filters: dict | None = None) -> list[Chunk]:
        q = np.array([vector], dtype="float32")
        scores, idxs = self._index.search(q, k)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1 or score < cfg.retrieval.score_threshold:
                continue
            chunk = self._chunks[idx]
            if filters and not _matches(chunk, filters):
                continue
            results.append(chunk)
        return results

    def count(self) -> int:
        return self._index.ntotal

    def delete_collection(self) -> None:
        self._index.reset()
        self._chunks.clear()


def _matches(chunk: Chunk, filters: dict) -> bool:
    return all(getattr(chunk, key, None) == val for key, val in filters.items())
