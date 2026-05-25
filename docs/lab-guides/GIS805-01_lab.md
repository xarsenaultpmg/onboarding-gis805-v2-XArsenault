# GIS805 — Séance 01 / 14 — NexaMart kickoff : pourquoi l'organisation ne peut pas répondre à ses propres questions

> Guide de studio (version Markdown). PDF équivalent : `docs/lab-guides/GIS805-01_lab.pdf`.

## En bref

- **Date :** 4 mai 2026
- **Horaire :** 19 h 00 – 22 h 00
- **Lieu :** Longueuil
- **Temps estimé :** 120 min (~2.0 h)

## Objectif

Comprendre pourquoi les systèmes opérationnels ne répondent pas aux questions stratégiques. Onboarding en classe : créer le repo, générer les données, rencontrer l'assistant IA. Lancer la simulation NexaMart et publier le premier board brief.

## Question du CEO

> « Quelles catégories déclinent dans quelles régions et pourquoi ? Chaque étudiant doit identifier sa première question exécutive. »

## Contexte du soir

**NexaMart S01 : Quelles catégories déclinent dans quelles régions et pourquoi ?**

Vous êtes le Head of Data de NexaMart Group. Le CEO veut savoir quelles catégories déclinent par région et par trimestre, mais les systèmes actuels ne permettent pas de répondre. Vous êtes seul responsable de l'ensemble de l'entrepôt : ventes, opérations, finance, marketing et expérience client.

## Résultats d'apprentissage

- Configurer son environnement de travail (Codespace ou VS Code) et générer ses données uniques en moins de 15 minutes.
- Interagir avec un assistant IA pour explorer un dépôt et comprendre sa structure.
- Diagnostiquer pourquoi les systèmes opérationnels ne sont pas conçus pour répondre de façon fiable et répétable à une question stratégique.
- Formuler une question d'affaires en termes de mesure, dimensions et hiérarchies.
- Rédiger un premier board brief identifiant votre question exécutive.

## Points clés

- Les systèmes OLTP sont conçus pour enregistrer, pas pour analyser.
- La pensée multidimensionnelle = mesures + dimensions + hiérarchies.
- NexaMart est votre entreprise pour tout le trimestre.

## Idées reçues à déjouer

  **Réalité :** Les données sont structurées pour enregistrer des transactions, pas pour répondre à dès questions stratégiques.
  **Réalité :** Un analyste peut répondre une fois. L'entrepôt rend la réponse répétable et fiable.

## Déroulé

### Partie 1 — Arrivee + CEO brief + Wooclap  *(10 min)*

Question CEO affichee a l'écran. Wooclap word cloud : nommez une question stratégique. Poll : quel est le plus grand obstacle pour obtenir des reponses fiables ?

### Partie 2 — Concepts + simulation NexaMart  *(20 min)*

Pourquoi les systèmes OLTP ne répondent pas aux questions stratégiques. Introduction de la pensee multidimensionnelle : mesures, dimensions, hiérarchies. Présentation de la simulation NexaMart. Chaque étudiant est le seul Head of Data de l'entreprise.

### Partie 3 — Onboarding sprint  *(20 min)*

Accepter l'assignment GitHub Classroom. Ouvrir un Codespace. Rencontrer l'assistant IA : "Qu'est-ce qui se trouve dans mon dépôt ?". Générer les données (make generate && make load && make check). Les étudiants qui finissent tot commencent a explorer.

### Partie 4 — Exploration diagnostique + debrief concepts  *(25 min)*

Explorer les données brutes dans DuckDB avec l'assistant IA : quelles tables existent ? Quelles colonnes ? Quelles questions peut-on poser vs ne peut-on PAS poser ? MCQs formatives (OLTP vs OLAP, definition d'une dimension). Correction des misconceptions (ERP = reponse, Excel = solution).

### Partie 5 — Premier board brief + demos  *(45 min)*

Chaque étudiant identifie sa question exécutive et redige le brief. 3-4 étudiants (au hasard) presentent : 2 min chacun -- question, reponse tentee, evidence, prochaine décision. Commit final + note ai-usage + exit ticket.

## Lab

**Objectif du lab :** Explore raw data with AI assistant, diagnose why operational data is not designed to answer the CEO question reliably at scale, publish first CEO brief.

**Livrable :** Exécutive board brief v1 + exploratory queries.

**Fichiers à produire (`repo_artifacts`) :**

- `answers/S01_executive_brief.md`
- `docs/board-briefs/s01-kickoff.md`
- `docs/problem-framing.md`
- `ai-usage.md`

## Remise

- **Échéance :** Before next session starts
- **Artefacts requis :**
  - `answers/S01_executive_brief.md`
  - `db/nexamart.duckdb`
  - `ai-usage.md`
- **Rubrique de notation :**
  - **model_quality** (40 %) — Grain et dimensions nommés dans le brief. fact_sales ou équivalent identifié avec au moins 3 dimensions.
  - **validation_quality** (25 %) — Seed pack chargé dans DuckDB. Au moins une requête exploratoire retourne un résultat non nul.
  - **executive_justification** (20 %) — Brief nomme la question CEO, les obstacles concrets, et la prochaine action.
  - **process_trace** (10 %) — Repo fonctionnel (S00 complete), données générées automatiquement. Note IA créée même si IA non utilisee.
  - **reproducibility** (5 %)

## Lectures

- [Kimball Group -- Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) — Référence des patterns dimensionnels fondamentaux (star schema, grain, faits, dimensions)
- [DuckDB Documentation -- Getting Started](https://duckdb.org/docs/) — Guide de démarrage pour le moteur analytique utilise dans le cours
- [dbt Labs -- Analytics Engineering Glossary](https://docs.getdbt.com/terms/dimensional-modeling) — Definition moderne de la modélisation dimensionnelle dans le contexte analytique

---

*Généré automatiquement à partir de `content/sessions/GIS805-01.yaml`. Pour corriger une coquille, modifiez le YAML source et poussez sur `master` — la CI régénère PDF + Markdown.*
