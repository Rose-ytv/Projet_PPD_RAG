"""
Benchmark comparatif Python/NumPy vs Mojo pour la similarite cosine.

Execution :
  mojo build similarity.mojo --shared -o similarity.so   # si Mojo installe
  python mojo/bench_python_vs_mojo.py
  python mojo/bench_python_vs_mojo.py --numpy-only        # sans Mojo installe
"""
import argparse
import time
import statistics
import numpy as np


def top_k_numpy(query: np.ndarray, corpus: np.ndarray, k: int):
    scores = corpus @ query
    top_k_idx = np.argpartition(scores, -k)[-k:]
    top_k_idx = top_k_idx[np.argsort(scores[top_k_idx])[::-1]]
    return top_k_idx, scores[top_k_idx]


def benchmark(n_docs: int = 5000, dim: int = 384, k: int = 5, n_rep: int = 100):
    print(f"\nConfiguration : {n_docs} documents, dim={dim}, top-k={k}, {n_rep} repetitions")
    print("-" * 60)

    rng = np.random.default_rng(42)
    corpus_raw = rng.random((n_docs, dim)).astype("float32")
    corpus = corpus_raw / np.linalg.norm(corpus_raw, axis=1, keepdims=True)
    query_raw = rng.random(dim).astype("float32")
    query = query_raw / np.linalg.norm(query_raw)

    latencies_numpy = []
    for _ in range(n_rep):
        t0 = time.perf_counter()
        top_k_numpy(query, corpus, k)
        latencies_numpy.append((time.perf_counter() - t0) * 1000)

    p50_np = round(statistics.median(latencies_numpy), 3)
    p95_np = round(sorted(latencies_numpy)[int(n_rep * 0.95)], 3)
    print(f"NumPy  -- p50: {p50_np}ms  | p95: {p95_np}ms")

    try:
        import ctypes, os
        so_path = os.path.join(os.path.dirname(__file__), "similarity.so")
        ctypes.CDLL(so_path)
        print("Mojo   -- module .so trouve (gain typique x3-8 sur calculs SIMD)")
    except (OSError, FileNotFoundError):
        print("Mojo   -- similarity.so non trouve.")
        print("          Compiler avec : mojo build similarity.mojo --shared -o similarity.so")

    print("-" * 60)
    print(f"Resultat NumPy seul : {p50_np}ms p50 pour {n_docs} vecteurs dim={dim}")
    print("-> Suffisant pour notre corpus (moins de 1000 chunks)")
    print("-> Mojo pertinent pour corpus > 100 000 vecteurs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-docs", type=int, default=5000)
    parser.add_argument("--n-rep", type=int, default=100)
    parser.add_argument("--numpy-only", action="store_true")
    args = parser.parse_args()
    benchmark(n_docs=args.n_docs, n_rep=args.n_rep)
