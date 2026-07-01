# ADR-004 — Choix du LLM et de la plateforme d'inference

## Date
Avril 2026 (revise Juin 2026)

## Statut
Accepte (revision -- explicite desormais la limite de souverainete)

## Contexte
Le LLM recoit la question et les chunks retrouves, et genere une reponse
en francais. Machine de developpement : Intel i3, 8 Go de RAM, dont
environ 800 Mo disponibles en cours d'execution.

## Options evaluees

| Critere | Ollama (local) | Groq (llama-3.1-8b-instant) |
|---|---|---|
| Vitesse | Tres lente sur cette machine | Quasi instantanee |
| Confidentialite / souverainete | Totale | Partielle |
| Dependance reseau | Aucune | Requiert internet |
| RAM requise | ~6 Go | Negligeable |
| Faisabilite sur la machine actuelle | Non (OOM ou 30-60s/reponse) | Oui |

## Decision
Groq (llama-3.1-8b-instant) pour le prototype.
Ollama code et documente comme alternative activable via config.yaml.

## Justification et limite assumee
Ce choix est un compromis materiel, pas une solution ideale. Il
**contredit partiellement** la problematique de souverainete des donnees
qui sous-tend le projet : chaque question (et les chunks retrouves)
transite par les serveurs de Groq. Ce n'est ni cache ni minimise : c'est
une consequence directe des contraintes materielles reelles de l'equipe.

Sur la machine de developpement, un modele local de la classe Mistral 7B
ou phi3 quantise produit des temps de reponse de plusieurs dizaines de
secondes ou des erreurs de memoire, incompatibles avec une demonstration
fluide en soutenance.

## Plan d'evolution
Sur un poste disposant de davantage de ressources (GPU ou 16 Go de RAM),
remplacer le LLM par Ollama en changeant un seul parametre dans
`config.yaml` (`llm.provider: ollama`). Le code supporte deja les deux
backends (`src/rag/generation/llm.py`).

## Consequences
- (+) Interface fluide pour les demonstrations.
- (+) Changement de backend = 1 parametre de configuration.
- (-) Data Residency partielle -- limite explicitement documentee.
- (-) Cle API a ne jamais committer (`.env` + `.gitignore`, cf. correction
  de securite appliquee en debut de projet).
