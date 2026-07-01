# ADR-001 — Choix de la base vectorielle

## Date
Avril 2026

## Statut
Accepté

## Contexte
Le système RAG nécessite une base de données capable de stocker et de 
rechercher efficacement des vecteurs de dimension 384. Trois solutions 
ont été évaluées : FAISS, Qdrant et Pgvector.

## Décision
Qdrant a été retenu comme base vectorielle principale du projet.

## Justification
Un benchmark a été réalisé sur 401 chunks issus du document AWS 
Well-Architected Sustainability Pillar avec les résultats suivants :

| Solution | Indexation | Recherche | Persistance | Production |
|---       |---         |---        |---          |---         |
| FAISS    | 0.002s     | 0.001s    | Non         | Non        |
| Qdrant   | 0.347s     | 0.018s    | Oui         | Oui        |
| Pgvector | 19.99s     | 0.068s    | Oui         | Partiel    |

FAISS est le plus rapide mais ne persiste pas les données — inadapté 
à un système en production.

Pgvector est trop lent à l'indexation car PostgreSQL n'est pas conçu 
nativement pour la recherche vectorielle.

Qdrant offre le meilleur compromis : rapide, persistant, conçu 
spécifiquement pour la recherche vectorielle et déployable via Docker.

## Alternatives rejetées
- **FAISS** — pas de persistance, pas d'API serveur
- **Pgvector** — indexation trop lente, complexité d'installation

## Conséquences
- Nécessite Docker pour le déploiement
- Les données survivent aux redémarrages
- Accessible depuis plusieurs applications simultanément

## Lien Green IT
Qdrant consomme moins de ressources que Pgvector grâce à son 
architecture native vectorielle, réduisant ainsi l'empreinte carbone 
du système.