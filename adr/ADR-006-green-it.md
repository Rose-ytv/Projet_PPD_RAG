# ADR-006 — Demarche Green IT

## Date
Avril 2026 (revise Juin 2026)

## Statut
Accepte (revision -- ajoute la limite methodologique)

## Contexte
Le projet s'inscrit dans une demarche de sobriete numerique coherente
avec le corpus documentaire utilise (AWS Well-Architected Sustainability
Pillar). L'empreinte carbone du systeme a ete mesuree avec la
bibliotheque CodeCarbon.

## Mesures obtenues

| Phase | Empreinte carbone |
|---|---|
| Indexation (une seule fois) | 0.011416 gCO2eq |
| Requete (par question) | 0.000599 gCO2eq |

A titre de comparaison, l'envoi d'un email represente environ 4 gCO2eq.
Une requete au systeme RAG consomme, sur la partie mesuree, environ 6600
fois moins qu'un email.

## Correction par rapport a la version initiale de cet ADR
La version initiale presentait ces chiffres sans aucune reserve. Or
**CodeCarbon ne capture que la consommation du processeur local**. Avec
le provider Groq (cf. ADR-004), l'inference du LLM se deroule sur des
serveurs distants et n'est donc **pas comptabilisee** dans les chiffres
ci-dessus : ces mesures **sous-estiment** l'empreinte reelle du systeme.

D'apres la litterature (Luccioni et al., 2023), l'inference d'un LLM 8B
sur GPU represente de l'ordre de 0.003 a 0.01 gCO2eq par requete -- un
ordre de grandeur du meme niveau que ce qui est mesure ici pour le reste
du pipeline, ce qui signifie que l'empreinte totale reelle est
probablement superieure de 50% a plusieurs fois aux chiffres publies.

## Choix techniques justifies par le Green IT

| Choix | Impact Green IT |
|---|---|
| Modele d'embedding leger (118 Mo) | Reduction de la consommation CPU |
| Cache d'embeddings par hash | Aucune revectorisation des chunks inchanges |
| Chunking optimise (500 caracteres) | Reduction des tokens traites par requete |
| Filtrage des questions hors sujet | Elimination des appels LLM inutiles |
| Indexation unique | La phase la plus couteuse ne se repete pas |

## Solution pour une mesure exhaustive
Basculer `llm.provider` sur `ollama` (cf. ADR-004) rend l'ensemble de la
chaine -- y compris la generation -- mesurable par CodeCarbon.

## Consequences
- Le systeme est mesurable et auditable en termes d'impact carbone.
- Les chiffres publies sont des **bornes basses**, explicitement
  documentees comme telles : la rigueur de la demarche Green IT impose
  de reconnaitre les angles morts de l'instrumentation autant que
  d'afficher des resultats favorables.

## References
- AWS Well-Architected Sustainability Pillar
- CodeCarbon — bibliotheque de mesure d'empreinte carbone
- Luccioni, A. et al. — Estimating the Carbon Footprint of BLOOM, 2023
- Greenhouse Gas Protocol — standard de comptabilite carbone
