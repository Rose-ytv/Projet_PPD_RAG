"""
Indexe tous les documents de data/corpus/ en une seule commande.
Usage : python scripts/ingest_corpus.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.pipeline import RagPipeline

CORPUS_DIR = Path("data/corpus")


def main():
    pdfs = list(CORPUS_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"[ingest] Aucun PDF trouve dans {CORPUS_DIR}")
        return

    print(f"[ingest] {len(pdfs)} fichier(s) a indexer")
    pipeline = RagPipeline()
    total = 0
    for pdf in pdfs:
        n = pipeline.ingest(str(pdf))
        total += n

    print(f"\n[ingest] Termine -- {total} chunks indexes au total")
    print(f"[ingest] Total dans le store : {pipeline.count()} chunks")


if __name__ == "__main__":
    main()
