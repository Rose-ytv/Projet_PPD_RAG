"""
Tests de recette -- verifient les criteres d'acceptation du cahier des
charges. Absent du projet original (aucun test automatise).
Lancer : pytest tests/recette/ -v
"""
import pytest
import os
from src.rag.ingestion.extract import extract_pages
from src.rag.ingestion.chunking import chunk_pages
from src.rag.embedding.embedder import Embedder
from src.rag.stores.faiss_store import FaissStore
from src.rag.generation.prompts import is_out_of_scope

PDF = "data/corpus/wellarchitected-sustainability-pillar.pdf"


@pytest.fixture(scope="module")
def full_pipeline():
    if not os.path.exists(PDF):
        pytest.skip(f"PDF absent : {PDF}")
    embedder = Embedder()
    store = FaissStore()
    pages = extract_pages(PDF)
    chunks = chunk_pages(pages)
    vectors = embedder.embed_texts([c.text for c in chunks])
    store.upsert(chunks, vectors)
    yield embedder, store, chunks
    store.delete_collection()


def test_F01_ingestion_chunks_avec_metadonnees(full_pipeline):
    _, _, chunks = full_pipeline
    assert len(chunks) > 100
    for c in chunks[:20]:
        assert c.text.strip()
        assert c.source.endswith(".pdf")
        assert c.page >= 1
        assert c.section


def test_F03_recherche_crosslingue_fr_en(full_pipeline):
    embedder, store, _ = full_pipeline
    q_vec = embedder.embed_query("Reduire l'empreinte carbone de mes workloads cloud")
    results = store.search(q_vec, k=5)
    assert len(results) > 0
    keywords = ["sustain", "carbon", "energy", "emission", "footprint"]
    assert any(any(kw in c.text.lower() for kw in keywords) for c in results)


def test_F04_chunks_retournent_sources(full_pipeline):
    embedder, store, _ = full_pipeline
    vec = embedder.embed_query("sustainability best practices AWS")
    results = store.search(vec, k=5)
    for c in results:
        assert c.source and c.page >= 1 and c.section


def test_F05_question_hors_domaine_refusee():
    for q in ["Quelle est la capitale de l'Australie ?", "Donne-moi une recette de gateau"]:
        assert is_out_of_scope(q)


def test_F05_question_dans_domaine_non_refusee():
    for q in ["Comment reduire l'empreinte carbone de mes workloads AWS ?",
              "Quelles best practices pour la durabilite dans le cloud ?"]:
        assert not is_out_of_scope(q)


def test_NF04_recall_minimum(full_pipeline):
    embedder, store, _ = full_pipeline
    test_questions = [
        ("Scale workload infrastructure dynamically", "SUS02-BP01"),
        ("Remove unused assets", "SUS02-BP03"),
        ("Use managed services", "SUS05-BP03"),
        ("Data classification policy", "SUS04-BP01"),
    ]
    recalls = []
    for q, expected in test_questions:
        vec = embedder.embed_query(q)
        results = store.search(vec, k=5)
        found = any(expected.lower() in c.section.lower() or expected.lower() in c.text.lower()
                    for c in results)
        recalls.append(1.0 if found else 0.0)
    assert sum(recalls) / len(recalls) >= 0.70
