"""
Interface CLI pour interroger le systeme RAG.
Usage : python scripts/ask.py "votre question"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.pipeline import RagPipeline


def main():
    if len(sys.argv) < 2:
        print('Usage : python scripts/ask.py "votre question"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    print(f"\nQuestion : {question}\n")

    pipeline = RagPipeline()
    reponse, chunks = pipeline.ask(question)

    print("Reponse :")
    print(reponse)

    if chunks:
        print(f"\nSources utilisees ({len(chunks)} chunks) :")
        for i, c in enumerate(chunks, 1):
            print(f"  [{i}] {c.source} - {c.section} - page {c.page}")


if __name__ == "__main__":
    main()
