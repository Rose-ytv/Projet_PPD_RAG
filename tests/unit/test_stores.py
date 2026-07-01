"""Tests unitaires -- contrat VectorStore (FAISS, pas besoin de Docker)."""
import pytest
from src.rag.stores.faiss_store import FaissStore


class TestFaissStore:
    @pytest.fixture
    def store(self):
        s = FaissStore()
        yield s
        s.delete_collection()

    def test_upsert_et_count(self, store, sample_chunks, sample_vectors):
        assert store.count() == 0
        store.upsert(sample_chunks, sample_vectors)
        assert store.count() == len(sample_chunks)

    def test_search_retourne_des_chunks(self, store, sample_chunks, sample_vectors):
        store.upsert(sample_chunks, sample_vectors)
        results = store.search(sample_vectors[0], k=3)
        assert 0 < len(results) <= 3

    def test_chunk_a_tous_les_champs(self, store, sample_chunks, sample_vectors):
        store.upsert(sample_chunks, sample_vectors)
        c = store.search(sample_vectors[0], k=1)[0]
        assert c.text and c.source and c.section
        assert isinstance(c.page, int)

    def test_delete_collection(self, store, sample_chunks, sample_vectors):
        store.upsert(sample_chunks, sample_vectors)
        store.delete_collection()
        assert store.count() == 0
