"""
Decoupage des pages en chunks (chunk_size=500, overlap=50 -- ADR-005).
CORRECTION : chaque chunk porte maintenant ses metadonnees completes
(source, page, section, bp_code), ce qui permet les citations sourcees
dans la reponse generee -- absent du projet original.
"""
import re
import uuid
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag.config import cfg

_BP_PATTERN = re.compile(r"(SUS\d{2}-BP\d{2})")


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    page: int
    section: str
    chunk_index: int
    bp_code: str | None = None


def chunk_pages(pages: list[dict]) -> list[Chunk]:
    """Decoupe la liste de pages (extract.py) en une liste de Chunk."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunking.chunk_size,
        chunk_overlap=cfg.chunking.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: list[Chunk] = []
    for page in pages:
        raw_chunks = splitter.split_text(page["text"])
        for i, text in enumerate(raw_chunks):
            if len(text.strip()) < 30:
                continue
            bp = _BP_PATTERN.search(text)
            all_chunks.append(Chunk(
                id=str(uuid.uuid4()),
                text=text.strip(),
                source=page["source"],
                page=page["page"],
                section=_detect_section(text),
                chunk_index=i,
                bp_code=bp.group(1) if bp else None,
            ))

    print(f"[chunk] {len(all_chunks)} chunks produits "
          f"(taille={cfg.chunking.chunk_size}, overlap={cfg.chunking.chunk_overlap})")
    return all_chunks


def _detect_section(text: str) -> str:
    """Extrait le titre de section le plus proche dans le texte du chunk."""
    bp = _BP_PATTERN.search(text)
    if bp:
        start = bp.start()
        end = min(start + 80, len(text))
        return text[start:end].split("\n")[0].strip()
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 10:
            return line[:80]
    return "Document"
