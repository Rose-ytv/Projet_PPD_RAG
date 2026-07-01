"""
Backend Qdrant -- base vectorielle principale (ADR-002).
CORRECTION : le payload original ne contenait que {"text": ...}.
Il porte maintenant source/page/section/bp_code, ce qui permet le
filtrage par metadonnees et les citations sourcees.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
)

from src.rag.config import cfg
from src.rag.ingestion.chunking import Chunk
from src.rag.stores.base import VectorStore


class QdrantStore(VectorStore):
    def __init__(self, collection: str | None = None):
        self._col = collection or cfg.stores.qdrant_collection
        self._client = QdrantClient(url=cfg.stores.qdrant_url)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if not self._client.collection_exists(self._col):
            self._client.create_collection(
                self._col,
                vectors_config=VectorParams(size=cfg.embedding.dimension, distance=Distance.COSINE),
            )
            print(f"[qdrant] Collection '{self._col}' creee (dim={cfg.embedding.dimension})")

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        points = [
            PointStruct(
                id=c.id,
                vector=v,
                payload={
                    "text": c.text,
                    "source": c.source,
                    "page": c.page,
                    "section": c.section,
                    "chunk_index": c.chunk_index,
                    "bp_code": c.bp_code or "",
                },
            )
            for c, v in zip(chunks, vectors)
        ]
        batch_size = 100
        for start in range(0, len(points), batch_size):
            self._client.upsert(self._col, points=points[start:start + batch_size])
        print(f"[qdrant] {len(chunks)} chunks indexes dans '{self._col}'")

    def search(self, vector: list[float], k: int, filters: dict | None = None) -> list[Chunk]:
        flt = None
        if filters:
            flt = Filter(must=[
                FieldCondition(key=key, match=MatchValue(value=val))
                for key, val in filters.items()
            ])

        hits = self._client.search(
    collection_name=self._col,
    query_vector=vector,
    limit=k,
    query_filter=flt,
    score_threshold=cfg.retrieval.score_threshold,
)

        return [
            Chunk(
                id=str(h.id),
                text=h.payload["text"],
                source=h.payload.get("source", "?"),
                page=h.payload.get("page", 0),
                section=h.payload.get("section", "?"),
                chunk_index=h.payload.get("chunk_index", 0),
                bp_code=h.payload.get("bp_code") or None,
            )
            for h in hits
        ]

    def count(self) -> int:
        info = self._client.get_collection(self._col)
        return info.points_count or 0

    def delete_collection(self) -> None:
        if self._client.collection_exists(self._col):
            self._client.delete_collection(self._col)
            print(f"[qdrant] Collection '{self._col}' supprimee")
