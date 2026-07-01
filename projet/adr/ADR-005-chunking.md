# ADR-004 — Stratégie de chunking

## Date
Avril 2026

## Statut
Accepté

## Contexte
Le document AWS Well-Architected Sustainability Pillar compte 97 pages. 
Il est impossible de l'envoyer intégralement au LLM en raison des 
limites de contexte et du coût énergétique associé. Le document doit 
donc être découpé en morceaux (chunks) avant indexation.

## Décision
Un découpage récursif par caractères avec une taille de 500 caractères 
et un chevauchement de 50 caractères a été retenu.

## Justification
Quatre stratégies ont été évaluées :

| Stratégie      | Avantages                | Inconvénients                        |
|---             |---                       |---                                   |
| Taille fixe    | Simple, rapide           | Coupe parfois au milieu d'une phrase |
| Par phrase     | Respecte la syntaxe      | Chunks trop petits                   |
| Par paragraphe | Respecte la structure    | Chunks trop variables en taille      |
| Récursif       | Equilibre taille et sens | Légèrement plus complexe             |

Le découpage récursif tente d'abord de couper aux paragraphes, puis 
aux phrases, puis aux mots si nécessaire. Il produit des chunks 
cohérents et de taille homogène.

Le paramètre chunk_size=500 a été choisi car il représente un bon 
équilibre entre contexte suffisant et précision de la recherche. 
Un chunk trop grand dilue le signal sémantique, un chunk trop petit 
perd le contexte.

Le chevauchement de 50 caractères garantit que le contexte n'est pas 
perdu entre deux chunks consécutifs.

## Résultat
Le document de 97 pages a été découpé en 401 chunks cohérents.

## Alternatives rejetées
- **Chunks de 1000 caractères** — trop de bruit dans la recherche
- **Chunks de 200 caractères** — perte de contexte, réponses incomplètes
- **Découpage par page** — trop hétérogène, certaines pages très denses

## Conséquences
- 401 vecteurs stockés dans Qdrant
- Temps d'indexation maîtrisé
- Qualité de recherche satisfaisante

## Lien Green IT
Des chunks de taille optimisée réduisent le nombre de tokens envoyés 
au LLM à chaque requête. Moins de tokens signifie moins de calcul, 
donc moins de consommation énergétique par requête.