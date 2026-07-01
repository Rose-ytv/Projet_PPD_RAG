"""
Mesure de l'empreinte carbone du systeme RAG.
CORRECTION : le green_it.py original ne signalait jamais que codecarbon
ne capture que le CPU local. Avec Groq (LLM distant), l'inference n'est
PAS mesuree -- les chiffres obtenus sous-estiment l'empreinte reelle.
Cette limite est desormais explicite dans la sortie du script.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from codecarbon import EmissionsTracker

from src.rag.config import cfg
from src.rag.pipeline import RagPipeline


def measure():
    print("=" * 55)
    print("  MESURE GREEN IT -- EMPREINTE CARBONE")
    print("=" * 55)

    print("\nPerimetre de la mesure :")
    if cfg.llm.provider == "groq":
        print("   - Embedding (local CPU) : mesure")
        print("   - Recherche vectorielle (local CPU) : mesuree")
        print("   - Inference LLM Groq (serveurs distants) : NON mesuree")
        print("   -> Pour une mesure complete, configurer llm.provider = ollama")
    else:
        print("   - Tout le pipeline (CPU local) : mesure")

    pipeline = RagPipeline()

    print("\n[green_it] Mesure phase d'indexation...")
    tracker_idx = EmissionsTracker(project_name="RAG_indexation", log_level="error", save_to_file=False)
    tracker_idx.start()
    n = pipeline.ingest("data/corpus/wellarchitected-sustainability-pillar.pdf")
    emissions_idx = tracker_idx.stop()

    print("[green_it] Mesure phase de requetes (10 questions)...")
    questions = [
        "Quels sont les principes de durabilite dans le cloud AWS ?",
        "Comment reduire la consommation energetique de mes workloads ?",
        "How to choose a region based on sustainability goals ?",
        "Quelles best practices pour la gestion des donnees ?",
        "Comment supprimer les ressources inutilisees ?",
        "What is predictive scaling and how does it help sustainability ?",
        "Quels types d'instances utiliser pour minimiser l'impact carbone ?",
        "Comment mesurer l'empreinte carbone de mes workloads AWS ?",
        "How to implement buffering to flatten the demand curve ?",
        "Quels sont les KPIs de durabilite recommandes par AWS ?",
    ]

    tracker_req = EmissionsTracker(project_name="RAG_requetes", log_level="error", save_to_file=False)
    tracker_req.start()
    for q in questions:
        pipeline.ask(q)
    emissions_req = tracker_req.stop()

    per_query = emissions_req / len(questions) if emissions_req else 0

    print(f"\n{'='*55}\n  RAPPORT GREEN IT\n{'='*55}")
    print(f"  Indexation ({n} chunks)  : {emissions_idx * 1000:.6f} gCO2eq")
    print(f"  Par requete (moyenne)   : {per_query * 1000:.6f} gCO2eq")
    print(f"  10 requetes total       : {emissions_req * 1000:.6f} gCO2eq")
    print()
    EMAIL_CO2 = 4.0
    ratio = EMAIL_CO2 / (per_query * 1000) if per_query > 0 else 0
    print(f"  Comparaison : 1 email ~ {EMAIL_CO2} gCO2eq")
    print(f"  -> 1 requete RAG ~ {ratio:.0f}x moins qu'un email")
    print()
    if cfg.llm.provider == "groq":
        print("  RAPPEL : inference LLM Groq non incluse dans ces chiffres.")
        print("  Ces mesures sous-estiment l'empreinte reelle du systeme.")

    return {
        "provider": cfg.llm.provider, "n_chunks": n,
        "indexation_gco2eq": round(emissions_idx * 1000, 6),
        "par_requete_gco2eq": round(per_query * 1000, 6),
        "10_requetes_gco2eq": round(emissions_req * 1000, 6),
        "inference_llm_mesuree": cfg.llm.provider == "ollama",
        "limite_methodologique": (
            "Inference LLM Groq (cloud) non capturee par codecarbon."
            if cfg.llm.provider == "groq" else None
        ),
    }


if __name__ == "__main__":
    measure()
