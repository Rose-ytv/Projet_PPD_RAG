"""Fixtures pytest partagees."""
import pytest
from src.rag.ingestion.chunking import Chunk


@pytest.fixture
def sample_chunks() -> list[Chunk]:
    """10 chunks fictifs pour les tests (pas besoin du vrai PDF)."""
    return [
        Chunk(
            id=f"test-{i:03d}",
            text=f"SUS0{i}-BP0{i} This best practice explains how to reduce energy "
                 f"consumption in cloud workloads. Section {i} content here.",
            source="wellarchitected-sustainability-pillar.pdf",
            page=i + 1,
            section=f"SUS0{i}-BP0{i} Reduce energy",
            chunk_index=i,
            bp_code=f"SUS0{i}-BP0{i}",
        )
        for i in range(1, 11)
    ]


@pytest.fixture
def sample_vectors() -> list[list[float]]:
    """Vecteurs aleatoires normalises (dimension 384)."""
    import numpy as np
    rng = np.random.default_rng(42)
    vecs = rng.random((10, 384)).astype("float32")
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return (vecs / norms).tolist()
