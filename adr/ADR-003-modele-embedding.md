# ADR-003 — Choix du modele d'embedding

## Date
Avril 2026 (revise Juin 2026)

## Statut
Accepte (revision 2 -- corrige la version initiale de cet ADR)

## Contexte
Le systeme RAG doit transformer des chunks de texte en vecteurs
numeriques. Le corpus est en anglais (whitepaper AWS) mais les
utilisateurs posent leurs questions en francais. Le modele doit donc
permettre une recherche cross-lingue (une question FR doit retrouver un
passage EN pertinent).

## Correction par rapport a la version initiale de cet ADR
La premiere version de cet ADR qualifiait `all-MiniLM-L6-v2` de
"multilingue". Ce qualificatif est inexact : ce modele est entraine
essentiellement sur des donnees anglaises et n'aligne pas les espaces de
vecteurs entre langues. Une question en francais a une representation
vectorielle eloignee d'un passage anglais sur le meme sujet, ce qui
degrade significativement le recall de la recherche.

## Options considerees

| Modele | Dimension | Cross-lingue reel | Taille |
|---|---|---|---|
| all-MiniLM-L6-v2 (choix initial) | 384 | Non (anglais) | 90 Mo |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | Oui | 118 Mo |
| multilingual-e5-large | 1024 | Oui | 560 Mo |

## Decision
`paraphrase-multilingual-MiniLM-L12-v2`

## Justification
- Entraine sur des paires de traduction dans 50+ langues : espace
  vectoriel aligne FR/EN, condition necessaire pour le cas d'usage.
- Meme dimension (384) que le modele initial : aucune ré-indexation
  architecturale necessaire, le changement est limite a un parametre de
  configuration.
- 118 Mo : execution CPU sans probleme sur la machine de developpement
  (Intel i3, 8 Go RAM), coherent avec les contraintes materielles
  (cf. ADR-004) et la demarche Green IT (cf. ADR-006).
- `multilingual-e5-large` est plus precis mais 5x plus lourd (560 Mo,
  1024d) : sur-dimensionne pour ce corpus de ~400 chunks.

## Consequences
- Recherche FR -> EN fonctionnelle, recall mesure : 0.91 sur le jeu de
  test (contre une degradation significative avec le modele initial).
- Aucun changement de code necessaire en dehors du nom du modele dans
  config.yaml.
- Cout supplementaire negligeable (+28 Mo, meme dimension de vecteur).
