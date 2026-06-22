# Rétroaction automatisée -- S02 (Schéma en étoile, grain et dimensions conformes : le premier modèle NexaMart)

_Générée le 2026-06-22T14:48:08+00:00 -- Run `20260622T143846Z-6b9e33b9`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief s'exécute correctement et produit la forme attendue. Bon travail sur l'auto-validation.

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
SELECT
    p.category,
    s."région" AS region,
    d.quarter,
    SUM(f.revenue) AS total_sales,
    COUNT(*)       AS line_count
FROM fact_sales AS f
INNER JOIN dim_product AS p
    ON f.product_key = p.product_key
INNER JOIN dim_store AS s
    ON f.store_key = s.store_key
INNER JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY
    p.category,
    s."région",
    d.quarter
ORDER BY
    total_sales DESC;
```

</details>

- Colonnes retournées : `category, region, quarter, total_sales, line_count`
- Correspondance avec les colonnes attendues :
  - `category` → `category`
  - `region` → `region`
  - `quarter` → `quarter`
  - `revenue` → `total_sales`
- Présence de NULLs dans des colonnes de groupement : `category` =0, `region` =0, `quarter` =0. Pensez à documenter le traitement de ces cas.

## 2. Rétroaction pédagogique sur le brief

> Très bon brief : grain et étoile sont clairement définis, la preuve SQL et les contrôles soutiennent la réponse opérationnelle et la recommandation est actionnable. Améliorez la traçabilité (commits et note IA/validation) et ajoutez un script d'exécution automatisé pour faciliter l'intégration CI/R reproducibility.

### Observations par dimension

**Model quality**
- Observation : Le brief définit clairement le grain (1 ligne = 1 ligne de commande) et décrit une étoile à cinq dimensions avec mesures `quantity` et `revenue`.
- Piste d'amélioration : Ajouter une phrase concise justifiant explicitement le choix des clés substituts vs clés naturelles pour anticiper les questions d'intégration ETL.

**Validation quality**
- Observation : Le SQL fourni agrège par category, région et quarter et le tableau de contrôles indique 'Orphelins ... 0' et 'Grain ... Conforme'.
- Piste d'amélioration : Inclure un test automatique (script .sql ou .py) qui exécute les checks et renvoie un code de sortie pour intégration CI.

**Executive justification**
- Observation : La section 'Réponse au CEO' explique en langage décisionnel que l'étoile rend la métrique répétable, identifie concentrations et propose une recommandation claire (industrialiser la requête, investiguer baisses >20%).
- Piste d'amélioration : Ajouter un indicateur chiffré (ex. : % du CA couvert par les 10 premières combinaisons) pour prioriser l'enquête opérationnelle.

**Process trace**
- Observation : Le brief mentionne des fichiers et un prompt IA pour générer le diagramme mais n'inclut pas d'historique git ni de note IA détaillée sur validation humaine.
- Piste d'amélioration : Ajouter un journal de décisions et au moins 3 commits significatifs dans le repo, plus une note IA précisant l'outil utilisé et comment les résultats ont été validés manuellement.

**Reproducibility**
- Observation : Des chemins de fichiers et le fichier canonique sql/analysis/s02-first-answer.sql sont référencés, permettant de reproduire l'analyse avec peu d'ajustements.
- Piste d'amélioration : Fournir un README 'Reproduce in 5 minutes' indiquant les commandes exactes (ex. clone, lancer DuckDB, exécuter checks.sql) et corriger tout chemin relatif si besoin.

## 3. Déclaration d'utilisation de l'IA

> La déclaration documente clairement quels modèles ont été utilisés et à quelles étapes, ainsi que des méthodes de validation humaines reproductibles. En revanche elle ne décrit pas explicitement les limites, erreurs ou comportements inattendus observés dans les sorties des outils IA.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain

**Sujets à ajouter ou expliciter pour la prochaine itération :**

- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Compléter i-usage.md en y ajoutant : limites ou erreurs observées.

---

## 5. Traçabilité

- **Run ID :** `20260622T143846Z-6b9e33b9`
- **Devoir :** `S02`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `944f5df`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T143846Z-6b9e33b9/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
