"""
Vectorisation des chunks et des requetes (ADR-003 -- CORRECTION).

PROBLEME ORIGINAL : le projet utilisait all-MiniLM-L6-v2, qualifie a tort
de "multilingue" dans l'ADR-002 d'origine. Ce modele est entraine
essentiellement sur de l'anglais : une question posee en francais est mal
alignee avec les passages anglais du corpus, ce qui degrade fortement le
recall de la recherche.

CORRECTION : paraphrase-multilingual-MiniLM-L12-v2, entraine sur des paires
de traduction dans 50+ langues. Meme dimension (384) que l'original, donc
aucune autre partie de l'architecture (Qdrant, FAISS, Pgvector) n'a besoin
d'etre modifiee.

Cache : hash SHA-256 du texte -> on ne revectorise jamais un chunk
inchange lors des re-ingestions (cf. ADR-006, demarche Green IT).
"""
import hashlib
import logging
import os
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.config import cfg

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


class Embedder:
    def __init__(self):
        print(f"[embedder] Chargement du modele {cfg.embedding.model}...")
        self.model = SentenceTransformer(cfg.embedding.model, device="cpu")
        self._cache_dir = Path(cfg.embedding.cache_dir)
        self._cache_dir.mkdir(exist_ok=True)

    def _cache_path(self, text: str) -> Path:
        h = hashlib.sha256(text.encode()).hexdigest()
        return self._cache_dir / f"{h}.npy"

    def _load_cache(self, text: str):
        p = self._cache_path(text)
        return np.load(str(p)) if p.exists() else None

    def _save_cache(self, text: str, vec) -> None:
        np.save(str(self._cache_path(text)), vec)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Vectorise une liste de chunks a indexer, avec cache."""
        results: list = [None] * len(texts)
        to_compute: list[tuple[int, str]] = []

        for i, t in enumerate(texts):
            cached = self._load_cache(t)
            if cached is not None:
                results[i] = cached.tolist()
            else:
                to_compute.append((i, t))

        if to_compute:
            idxs, txts = zip(*to_compute)
            vecs = self.model.encode(
                list(txts),
                batch_size=cfg.embedding.batch_size,
                show_progress_bar=True,
                normalize_embeddings=True,
            )
            for idx, vec in zip(idxs, vecs):
                self._save_cache(texts[idx], vec)
                results[idx] = vec.tolist()

        hit_count = len(texts) - len(to_compute)
        if hit_count:
            print(f"[embedder] Cache : {hit_count}/{len(texts)} chunks deja calcules")

        return results

    def embed_query(self, question: str) -> list[float]:
        """Vectorise une question utilisateur."""
        vec = self.model.encode(question, normalize_embeddings=True)
        return vec.tolist()

    @property
    def dimension(self) -> int:
        return cfg.embedding.dimension
