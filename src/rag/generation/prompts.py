from src.rag.ingestion.chunking import Chunk

SYSTEM_PROMPT = """You are an expert assistant in AWS Cloud Architecture, specialized in digital sustainability.

STRICT RULES:
1. Answer ONLY using the context snippets provided below.
2. ALWAYS cite your sources using square brackets: [filename - section - page N].
3. If the context snippets do not contain the answer to the question, state clearly that you cannot find the answer in the provided documents, but do so in the SAME language as the user's question.

MANDATORY LANGUAGE RULE:
- You must detect the language of the user's question and reply exclusively in that SAME language.
- If the question is in English, your entire response MUST be in English (including the "I cannot find the answer" statement).
- If the question is in French, your entire response MUST be in French.
Never mix languages.
"""

# Ce message n'est utilisé que pour les hors-sujets complets (ex: "hello")
OUT_OF_SCOPE_RESPONSE = (
    "Cette entrée n'est pas valide. / This input is invalid. "
    "I am a RAG assistant specialized only in AWS Cloud & digital sustainability."
)

def build_prompt(question: str, chunks: list[Chunk]) -> str:
    """Construit uniquement la partie CONTEXTE et QUESTION pour l'utilisateur."""
    context_parts = []
    for i, c in enumerate(chunks, 1):
        label = f"[{c.source} - {c.section} - page {c.page}]"
        context_parts.append(f"Snippet {i} {label}\n{c.text}")

    context = "\n\n---\n\n".join(context_parts)

    return (
        f"CONTEXT SNIPPETS:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        f"RESPONSE (cite sources in brackets):"
    )

def is_out_of_scope(question: str) -> bool:
    """Detection lexicale legere des questions hors domaine."""
    keywords = [
        "cloud", "aws", "architecture", "sustainability", "durabilite",
        "sobriete", "numerique", "data", "edge", "hybride", "multi-cloud",
        "serveur", "deploiement", "infrastructure", "carbone", "energie",
        "qdrant", "embedding", "rag", "azure", "gcp", "system"
    ]
    q_lower = question.lower()
    return not any(kw in q_lower for kw in keywords)
