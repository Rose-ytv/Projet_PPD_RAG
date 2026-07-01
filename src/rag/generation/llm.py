"""
Client LLM -- Groq (defaut, comme le projet original) + Ollama (local).

Note assumee dans l'ADR-004 : Groq envoie la question et les chunks vers
des serveurs distants, ce qui contredit partiellement la problematique de
souverainete des donnees du projet. C'est un compromis materiel assume
(machine de developpement limitee), pas une solution ideale.
Ollama, 100% local, est code et disponible en alternative via config.yaml.
"""
import requests
from groq import Groq

from src.rag.config import cfg, GROQ_API_KEY
from src.rag.generation.prompts import build_prompt
from src.rag.ingestion.chunking import Chunk


def generate(question: str, chunks: list[Chunk]) -> str:
    prompt = build_prompt(question, chunks)
    if cfg.llm.provider == "ollama":
        return _ollama(prompt)
    return _groq(prompt)


def _groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY manquant. Copier .env.example en .env et renseigner la cle."
        )
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=cfg.llm.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens,
    )
    return response.choices[0].message.content


def _ollama(prompt: str) -> str:
    """Generation 100% locale -- aucune donnee sortante."""
    response = requests.post(
        cfg.llm.ollama_url,
        json={
            "model": cfg.llm.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": cfg.llm.temperature, "num_predict": cfg.llm.max_tokens},
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"]
