"""
Orchestration principale du RAG.
CORRECTION MAJEURE : le projet original dupliquait le chargement PDF +
chunking + embedding dans indexation.py, benchmark.py ET green_it.py.
Desormais un seul endroit : RagPipeline.ingest() et RagPipeline.ask().
"""
from src.rag.config import cfg
from src.rag.ingestion.extract import extract_pages
from src.rag.ingestion.chunking import chunk_pages, Chunk
from src.rag.embedding.embedder import Embedder
from src.rag.generation.llm import generate
from src.rag.generation.prompts import is_out_of_scope, OUT_OF_SCOPE_RESPONSE
from src.rag.stores.base import VectorStore


def _make_store(backend: str | None = None) -> VectorStore:
    """Factory -- selectionne le backend via config.yaml ou parametre."""
    b = backend or cfg.stores.default_backend
    if b == "qdrant":
        from src.rag.stores.qdrant_store import QdrantStore
        return QdrantStore()
    if b == "faiss":
        from src.rag.stores.faiss_store import FaissStore
        return FaissStore()
    if b == "pgvector":
        from src.rag.stores.pgvector_store import PgvectorStore
        return PgvectorStore()
    raise ValueError(f"Backend inconnu : {b!r}. Valeurs valides : qdrant, faiss, pgvector")


class RagPipeline:
    """
    Pipeline RAG complet.

    Usage :
        rag = RagPipeline()
        rag.ingest("data/corpus/wellarchitected-sustainability-pillar.pdf")
        answer, sources = rag.ask("Quelles best practices pour reduire le CO2 ?")
    """

    def __init__(self, backend: str | None = None):
        self.embedder = Embedder()
        self.store = _make_store(backend)

    def ingest(self, pdf_path: str) -> int:
        """Indexe un document PDF. Retourne le nombre de chunks crees."""
        pages = extract_pages(pdf_path)
        chunks = chunk_pages(pages)
        vectors = self.embedder.embed_texts([c.text for c in chunks])
        self.store.upsert(chunks, vectors)
        print(f"[pipeline] Ingestion terminee -- {len(chunks)} chunks dans le store")
        return len(chunks)

    def ask(self, question: str, filters: dict | None = None) -> tuple[str, list[Chunk]]:
        """Repond a une question. Retourne (reponse_texte, chunks_utilises)."""
        if is_out_of_scope(question):
            return OUT_OF_SCOPE_RESPONSE, []

        q_vec = self.embedder.embed_query(question)
        chunks = self.store.search(q_vec, k=cfg.retrieval.top_k, filters=filters)

        if not chunks:
            return "Aucun passage pertinent trouve dans le corpus pour cette question.", []

        answer = generate(question, chunks)
        return answer, chunks

    def count(self) -> int:
        return self.store.count()
