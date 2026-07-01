# ADR-001 — Architecture generale : RAG plutot que fine-tuning

## Date
Juin 2026

## Statut
Accepte

## Contexte
Cet ADR etait absent du projet initial alors qu'il s'agit de la decision
la plus fondamentale du projet : pourquoi un RAG plutot qu'un fine-tuning
ou une recherche plein texte classique ? Le systeme doit repondre a des
questions sur un corpus documentaire technique qui evolue dans le temps
(nouvelles versions des whitepapers AWS).

## Options considerees

| Option | Avantages | Inconvenients |
|---|---|---|
| RAG | Corpus actualisable sans reentrainement, reponses sourcees | Latence de retrieval, qualite dependante du chunking |
| Fine-tuning | Reponses fluides | GPU requis, corpus fige, cout CO2 eleve |
| Recherche plein texte (BM25) | Rapide, deterministe | Ne capte pas la semantique cross-lingue |

## Decision
RAG (Retrieval-Augmented Generation).

## Justification
- Le corpus evolue : le RAG met a jour la connaissance par simple
  re-ingestion, sans reentrainement.
- Les reponses doivent citer leurs sources -- seul le RAG le permet
  naturellement.
- Le fine-tuning exige des GPU et plusieurs heures d'entrainement,
  incompatible avec les contraintes materielles du projet (cf. ADR-004).
- La recherche plein texte seule ne capte pas la semantique cross-lingue
  (FR -> EN), exigence centrale du projet.

## Consequences
- Corpus actualisable a chaud, reponses tracables.
- Qualite dependante du retrieval : chunking et embedding deviennent
  critiques (cf. ADR-003 et ADR-005).
- Latence superieure a un LLM seul (etape de retrieval), acceptable pour
  un outil d'aide a la decision non temps-reel.
