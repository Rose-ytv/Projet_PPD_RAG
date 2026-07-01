"""
Interface commune pour les 3 backends vectoriels (pattern Strategy).
Changer de backend = changer 1 ligne dans config.yaml, pas le code.
"""
from abc import ABC, abstractmethod
from src.rag.ingestion.chunking import Chunk


class VectorStore(ABC):

    @abstractmethod
    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Indexe des chunks avec leurs vecteurs."""

    @abstractmethod
    def search(self, vector: list[float], k: int, filters: dict | None = None) -> list[Chunk]:
        """Retourne les k chunks les plus proches du vecteur requete."""

    @abstractmethod
    def count(self) -> int:
        """Nombre de chunks indexes."""

    @abstractmethod
    def delete_collection(self) -> None:
        """Vide la collection (utile pour les tests)."""
