"""
Prompts systeme et construction du contexte injecte dans le LLM.
CORRECTION : le prompt original ne demandait aucune citation et le
payload Qdrant ne contenait pas les metadonnees necessaires pour le
faire. Desormais chaque extrait est labellise [source - section - page].
"""
from src.rag.ingestion.chunking import Chunk

SYSTEM_PROMPT = """Tu es un assistant expert en architecture Cloud AWS, specialise dans la \
sobriete numerique (sustainability).

Regles STRICTES :
1. Reponds UNIQUEMENT a partir des extraits fournis ci-dessous.
2. Cite TOUJOURS tes sources entre crochets : [nom_fichier - section - page N].
3. Si les extraits ne contiennent pas la reponse, dis-le explicitement.
4. Reponds en francais, meme si les extraits sont en anglais.
"""

OUT_OF_SCOPE_RESPONSE = (
    "Cette entree n'est pas valide. Je suis un assistant RAG specialise uniquement dans "
    "la gestion du Cloud AWS et la sobriete numerique. Veuillez poser une question "
    "specifique a ce domaine."
)


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    """Construit le prompt complet avec le contexte source."""
    context_parts = []
    for i, c in enumerate(chunks, 1):
        label = f"[{c.source} - {c.section} - page {c.page}]"
        context_parts.append(f"Extrait {i} {label}\n{c.text}")

    context = "\n\n---\n\n".join(context_parts)

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"EXTRAITS DE REFERENCE :\n{context}\n\n"
        f"QUESTION : {question}\n\n"
        f"REPONSE (cite les sources entre crochets) :"
    )


def is_out_of_scope(question: str) -> bool:
    """Detection lexicale legere des questions hors domaine."""
    keywords = [
        "cloud", "aws", "architecture", "sustainability", "durabilite",
        "sobriete", "numerique", "data", "edge", "hybride", "multi-cloud",
        "serveur", "deploiement", "infrastructure", "carbone", "energie",
        "qdrant", "embedding", "rag", "azure", "gcp",
    ]
    q_lower = question.lower()
    return not any(kw in q_lower for kw in keywords)
