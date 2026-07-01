"""
Tests unitaires -- module embedder.
Le test test_multilingue_fr_en() verifie precisement la correction de
l'etape 4 (modele realmente multilingue), absent du projet original.
"""
import pytest
from src.rag.config import cfg
from src.rag.embedding.embedder import Embedder


@pytest.fixture(scope="module")
def embedder():
    return Embedder()


class TestEmbedder:
    def test_dimension_vecteur(self, embedder):
        vecs = embedder.embed_texts(["Test sentence for embedding."])
        assert len(vecs[0]) == cfg.embedding.dimension

    def test_vecteur_normalise(self, embedder):
        import math
        vecs = embedder.embed_texts(["Normalized vector test."])
        norm = math.sqrt(sum(x**2 for x in vecs[0]))
        assert abs(norm - 1.0) < 1e-4

    def test_embed_query_dimension(self, embedder):
        vec = embedder.embed_query("Quels sont les principes de durabilite ?")
        assert len(vec) == cfg.embedding.dimension

    def test_multilingue_fr_en(self, embedder):
        """Une question FR doit etre proche semantiquement d'une phrase EN equivalente."""
        import numpy as np
        fr = embedder.embed_query("Reduire l'empreinte carbone du cloud")
        en = embedder.embed_query("Reduce the carbon footprint of cloud workloads")
        unrelated = embedder.embed_query("La recette de la tarte aux pommes")

        sim_fr_en = float(np.dot(fr, en))
        sim_fr_unrel = float(np.dot(fr, unrelated))
        assert sim_fr_en > sim_fr_unrel, (
            "Le modele multilingue doit aligner FR et EN sur le meme sujet"
        )
