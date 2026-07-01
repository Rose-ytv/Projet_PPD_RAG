# RAG — AWS Well-Architected Sustainability (version corrigee)

Systeme de Retrieval-Augmented Generation (RAG) permettant d'interroger
le document AWS Well-Architected Sustainability Pillar en langage naturel,
y compris en posant des questions en francais sur un corpus en anglais.

Ce projet est la version corrigee du projet original : modele d'embedding
reellement multilingue, citations sourcees, pipeline sans duplication,
benchmark instrumente, mesure Green IT avec ses limites documentees,
module Mojo, tests automatises. Le detail de chaque correction est dans
`adr/` (Architecture Decision Records).

---

## Architecture du systeme

```
Document PDF -> Extraction -> Chunking -> Embedding -> Qdrant
                                                          |
Question (FR) -> Embedding -> Recherche vectorielle -> LLM -> Reponse sourcee
```

## Technologies utilisees

| Composant          | Technologie                                  |
|---                  |---                                            |
| Langage             | Python 3.10+ (+ Mojo pour la similarite)      |
| Base vectorielle    | Qdrant (principal), FAISS, Pgvector (comparees)|
| Modele d'embedding  | paraphrase-multilingual-MiniLM-L12-v2 (FR/EN) |
| LLM                 | llama-3.1-8b-instant via Groq (Ollama en option)|
| Interface           | Flask + HTML/CSS                              |
| Mesure Green IT     | CodeCarbon                                    |
| Conteneurisation    | Docker                                        |

---

## Prerequis

- Python 3.10 ou superieur
- Docker installe et lance
- Une cle API Groq personnelle (gratuite sur https://console.groq.com)
  -- ne JAMAIS reutiliser une cle trouvee dans un ancien README, elle est compromise

---

## Installation (a faire une seule fois)

### 1. Creer et activer l'environnement virtuel

Sur les systemes Linux recents (Ubuntu 23.04+, Debian 12+), `pip install`
direct est bloque par le systeme : il faut imperativement passer par un
environnement virtuel.

```bash
python3 -m venv rag_env
source rag_env/bin/activate
```

Ton invite de commande doit maintenant commencer par `(rag_env)`.
Il faudra refaire ce `source rag_env/bin/activate` a chaque nouvelle
session de terminal, avant de lancer quoi que ce soit dans ce projet.

### 2. Installer les dependances

```bash
pip install -r requirements.txt
```

### 3. Configurer la cle API

```bash
cp .env.example .env
nano .env   # remplace "ta_cle_ici" par ta propre cle Groq
```

### 4. Lancer les bases de donnees

```bash
docker compose up -d
```

Cela demarre Qdrant (port 6333) et Pgvector (port 5433) en arriere-plan.

### 5. Indexer le document

```bash
python scripts/ingest_corpus.py
```

A faire une seule fois (ou a chaque modification du corpus dans
`data/corpus/`). Cela charge le PDF, le decoupe en chunks et stocke les
embeddings dans Qdrant.

---

## Lancement de l'application

```bash
source rag_env/bin/activate    # si ce n'est pas deja fait dans ce terminal
python app.py
```

Ouvre ensuite http://localhost:5000 dans ton navigateur.

---

## Structure du projet

```
rag-cloud-efficient/
├── app.py                      Serveur Flask
├── config.yaml                 Configuration centralisee
├── docker-compose.yml          Qdrant + Pgvector
├── requirements.txt
├── .env.example / .env
│
├── src/rag/
│   ├── ingestion/               Extraction PDF + decoupage en chunks
│   ├── embedding/                Vectorisation (modele multilingue)
│   ├── stores/                  Qdrant / FAISS / Pgvector (interface commune)
│   ├── generation/               Prompts + appel au LLM
│   └── pipeline.py               Orchestration ingest() / ask()
│
├── data/corpus/                  Le PDF source
├── templates/index.html          Interface web
│
├── benchmark/
│   ├── run_benchmark.py          Comparaison Qdrant / FAISS / Pgvector
│   └── carbon_tracking.py        Mesure de l'empreinte carbone
│
├── mojo/                         Module de similarite cosine optimise
├── adr/                          Architecture Decision Records (6 fichiers)
├── tests/                        Tests unitaires + de recette
└── scripts/
    ├── ingest_corpus.py
    └── ask.py                    Poser une question en ligne de commande
```

---

## Commandes utiles

```bash
# Poser une question directement en ligne de commande
python scripts/ask.py "Comment reduire l'empreinte carbone de mes workloads AWS ?"

# Lancer le benchmark des 3 bases vectorielles (Qdrant + Pgvector doivent tourner)
python benchmark/run_benchmark.py

# Mesurer l'empreinte carbone du systeme
python benchmark/carbon_tracking.py

# Lancer les tests automatises
pytest tests/unit -v          # rapides, sans Docker
pytest tests/recette -v       # necessitent le corpus indexe

# Comparer Python et Mojo sur le calcul de similarite
python mojo/bench_python_vs_mojo.py --numpy-only
```

---

## Choix techniques

Toutes les decisions d'architecture, y compris les corrections apportees
par rapport a la version initiale du projet, sont documentees dans le
dossier `adr/` sous forme d'Architecture Decision Records :

- **ADR-001** — Pourquoi un RAG plutot qu'un fine-tuning
- **ADR-002** — Choix de la base vectorielle (Qdrant)
- **ADR-003** — Modele d'embedding multilingue (corrige)
- **ADR-004** — Choix du LLM (Groq, limite de souverainete assumee)
- **ADR-005** — Strategie de decoupage (chunking)
- **ADR-006** — Demarche Green IT (limite methodologique documentee)

---

## Auteur

Projet realise dans le cadre du Master MIAGE M1
Universite Paris Cite — UFR Maths-Info
Encadrant : Gilles Poirot
