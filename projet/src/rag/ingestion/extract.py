"""
Extraction de texte depuis les fichiers PDF.
Conserve les metadonnees de page -- necessaire pour les citations
sourcees (CORRECTION : le projet original ne gardait aucune metadonnee).
"""
import re
from pathlib import Path
from pypdf import PdfReader


def extract_pages(pdf_path: str) -> list[dict]:
    """
    Retourne une liste de dicts {text, page, source}.
    Chaque dict correspond a une page du PDF avec ses metadonnees.
    """
    path = Path(pdf_path)
    reader = PdfReader(str(path))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = _clean(text)
        if len(text.strip()) > 50:
            pages.append({"text": text, "page": i + 1, "source": path.name})

    print(f"[extract] {path.name} -> {len(pages)} pages extraites")
    return pages


def _clean(text: str) -> str:
    """Supprime le bruit recurrent des whitepapers AWS."""
    text = re.sub(r"Sustainability Pillar\s+AWS Well-Architected Framework", "", text)
    text = re.sub(r"AWS Well-Architected Framework\s+Sustainability Pillar", "", text)
    text = re.sub(
        r"(Related (videos|documents|examples|trainings):.*?)(?=\n[A-Z#]|\Z)",
        "", text, flags=re.S,
    )
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
