"""
Benchmark des 3 backends vectoriels.
CORRECTION : le benchmark.py original ne mesurait qu'UNE SEULE requete,
UNE SEULE fois, sans recall. Desormais : 10 questions, 20 repetitions
chacune (p50/p95), et un recall@5 calcule sur des sections attendues.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import statistics
import time
import tracemalloc
from pathlib import Path

from src.rag.config import cfg
from src.rag.embedding.embedder import Embedder
from src.rag.ingestion.extract import extract_pages
from src.rag.ingestion.chunking import chunk_pages

QUESTIONS = [
    {"question": "Quels sont les principes de durabilite dans le cloud AWS ?",
     "sections_attendues": ["Design principles", "Sustainability in the cloud"]},
    {"question": "Comment reduire la consommation energetique de mes workloads ?",
     "sections_attendues": ["SUS02-BP01", "SUS05-BP01", "SUS05-BP02"]},
    {"question": "What are the best practices for data management sustainability ?",
     "sections_attendues": ["SUS04-BP01", "SUS04-BP03", "SUS04-BP05"]},
    {"question": "Comment choisir la region AWS pour minimiser l'impact carbone ?",
     "sections_attendues": ["SUS01-BP01", "Region selection"]},
    {"question": "Quelles sont les metriques de performance pour la durabilite ?",
     "sections_attendues": ["Key performance indicators", "Proxy metrics"]},
    {"question": "How to scale workloads efficiently to reduce environmental impact ?",
     "sections_attendues": ["SUS02-BP01"]},
    {"question": "Quels services manages AWS utilises pour la sobriete numerique ?",
     "sections_attendues": ["SUS05-BP03"]},
    {"question": "Comment supprimer les donnees inutiles pour reduire le stockage ?",
     "sections_attendues": ["SUS04-BP05", "SUS04-BP03"]},
    {"question": "What is the shared responsibility model for sustainability ?",
     "sections_attendues": ["The shared responsibility model"]},
    {"question": "Comment optimiser le code pour consommer moins de ressources ?",
     "sections_attendues": ["SUS03-BP03"]},
]

N_REP = cfg.benchmark.n_repetitions


def _recall_at_k(results, expected_sections):
    if not expected_sections:
        return 1.0
    found = 0
    for sec in expected_sections:
        for chunk in results:
            if sec.lower() in chunk.section.lower() or sec.lower() in chunk.text.lower():
                found += 1
                break
    return round(found / len(expected_sections), 3)


def benchmark_backend(backend, chunks, vectors, embedder):
    print(f"\n{'='*50}\n  BENCHMARK : {backend.upper()}\n{'='*50}")

    if backend == "qdrant":
        from src.rag.stores.qdrant_store import QdrantStore
        store = QdrantStore(collection=f"benchmark_{backend}")
    elif backend == "faiss":
        from src.rag.stores.faiss_store import FaissStore
        store = FaissStore()
    elif backend == "pgvector":
        from src.rag.stores.pgvector_store import PgvectorStore
        store = PgvectorStore()
        store.delete_collection()
    else:
        raise ValueError(f"Backend inconnu : {backend}")

    tracemalloc.start()
    t0 = time.perf_counter()
    store.upsert(chunks, vectors)
    t_index = round(time.perf_counter() - t0, 4)
    _, ram_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Indexation : {t_index}s | RAM pic : {ram_peak / 1e6:.1f} Mo")

    latencies, recalls = [], []
    for q_data in QUESTIONS:
        q_vec = embedder.embed_query(q_data["question"])
        q_latencies = []
        for _ in range(N_REP):
            t0 = time.perf_counter()
            results = store.search(q_vec, k=cfg.retrieval.top_k)
            q_latencies.append(time.perf_counter() - t0)
        latencies.extend(q_latencies)
        recalls.append(_recall_at_k(results, q_data["sections_attendues"]))

    all_ms = [t * 1000 for t in latencies]
    p50 = round(statistics.median(all_ms), 2)
    p95 = round(sorted(all_ms)[int(len(all_ms) * 0.95)], 2)
    mean_recall = round(statistics.mean(recalls), 3)

    print(f"  Latence p50 : {p50}ms | p95 : {p95}ms")
    print(f"  Recall@{cfg.retrieval.top_k} moyen : {mean_recall}")

    if backend in ("qdrant", "pgvector"):
        store.delete_collection()

    return {
        "backend": backend, "n_chunks": len(chunks), "indexation_s": t_index,
        "ram_peak_indexation_mo": round(ram_peak / 1e6, 1),
        "latence_p50_ms": p50, "latence_p95_ms": p95,
        f"recall_at_{cfg.retrieval.top_k}": mean_recall,
        "n_questions": len(QUESTIONS), "n_repetitions": N_REP,
    }


def main():
    print("\n[benchmark] Chargement et preparation des donnees...")
    pdf = "data/corpus/wellarchitected-sustainability-pillar.pdf"
    pages = extract_pages(pdf)
    chunks = chunk_pages(pages)
    embedder = Embedder()
    vectors = embedder.embed_texts([c.text for c in chunks])

    results = []
    for backend in ["faiss", "qdrant", "pgvector"]:
        try:
            results.append(benchmark_backend(backend, chunks, vectors, embedder))
        except Exception as e:
            print(f"[benchmark] {backend} ERREUR : {e}")

    print(f"\n{'='*60}\n  RESULTATS FINAUX\n{'='*60}")
    print(f"{'Backend':<12} {'Index(s)':<10} {'p50(ms)':<10} {'p95(ms)':<10} {'Recall@5':<10} {'RAM(Mo)'}")
    print("-" * 60)
    for r in results:
        print(f"{r['backend']:<12} {r['indexation_s']:<10} {r['latence_p50_ms']:<10} "
              f"{r['latence_p95_ms']:<10} {r[f'recall_at_{cfg.retrieval.top_k}']:<10} "
              f"{r['ram_peak_indexation_mo']}")

    out = Path("benchmark/results/benchmark_results.json")
    out.parent.mkdir(exist_ok=True, parents=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n[benchmark] Resultats sauvegardes dans {out}")


if __name__ == "__main__":
    main()
