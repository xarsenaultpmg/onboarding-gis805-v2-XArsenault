# Rétroaction automatisée -- S01 (Diagnostic fondamental -- NexaMart kickoff)

_Générée le 2026-05-14T22:23:35+00:00 -- Run `20260514T221333Z-7d34bf6a`_

Ce document est produit par un pipeline reproductible (vérification SQL déterministe + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief n'a pas pu être validée automatiquement. Quelques pistes constructives ci-dessous pour vous aider à la rendre exécutable et alignee avec la question posée.

_Observation technique : erreur d'exécution SQL: Parser Error: syntax error at or near "┌───────────┬───────────────────┬─────────┬─────────────┬────────────────────┬──────────┬────────────┐"_

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
WITH quarterly_sales AS (
    SELECT
        s.region
      , p.category
      , d.quarter
      , SUM(f.line_total) AS total_sales
    FROM raw_fact_sales f
    INNER JOIN raw_dim_product p ON f.product_id = p.product_id
    INNER JOIN raw_dim_store s ON f.store_id = s.store_id
    INNER JOIN raw_dim_date d ON f.order_date = d.date_key
    GROUP BY s.region, p.category, d.quarter
),
with_lag AS (
    SELECT
        *
      , LAG(total_sales) OVER (
            PARTITION BY region, category
            ORDER BY quarter
        ) AS prev_quarter_sales
      , total_sales - LAG(total_sales) OVER (
            PARTITION BY region, category
            ORDER BY quarter
        ) AS delta
    FROM quarterly_sales
)
SELECT
    region
  , category
  , quarter
  , ROUND(total_sales, 2)        AS total_sales
  , ROUND(prev_quarter_sales, 2) AS prev_quarter_sales
  , ROUND(delta, 2)              AS delta
  , ROUND(delta / prev_quarter_sales * 100, 1) AS pct_change
FROM with_lag
WHERE delta < 0
  AND prev_quarter_sales IS NOT NULL
ORDER BY pct_change ASC
LIMIT 10;

┌───────────┬───────────────────┬─────────┬─────────────┬────────────────────┬──────────┬────────────┐
│  region   │     category      │ quarter │ total_sales │ prev_quarter_sales │  delta   │ pct_change │
│  varchar  │      varchar      │  int64  │   double    │       double       │  double  │   double   │
├───────────┼───────────────────┼─────────┼─────────────┼────────────────────┼──────────┼────────────┤
│ Québec    │ Home & Garden     │       2 │      419.27 │            3294.37 │  -2875.1 │      -87.3 │
│ Estrie    │ Clothing          │       2 │       87.09 │             590.17 │  -503.08 │      -85.2 │
│ BC        │ Books & Media     │       3 │      804.34 │            5122.84 │  -4318.5 │      -84.3 │
│ Estrie    │ Sports & Outdoors │       4 │      235.67 │             996.98 │  -761.31 │      -76.4 │
│ Outaouais │ Electronics       │       2 │       288.7 │            1011.24 │  -722.54 │      -71.5 │
│ Estrie    │ Toys & Games      │       4 │      905.28 │            2899.11 │ -1993.83 │      -68.8 │
│ Ontario   │ Clothing          │       4 │     1034.37 │             3059.9 │ -2025.53 │      -66.2 │
│ Ontario   │ Home & Garden     │       2 │      1024.0 │            3001.14 │ -1977.14 │      -65.9 │
│ Alberta   │ Automotive        │       4 │     2580.39 │            7514.94 │ -4934.55 │      -65.7 │
│ BC        │ Beauty & Health   │       3 │      887.85 │            2492.47 │ -1604.62 │      -64.4 │
├───────────┴───────────────────┴─────────┴─────────────┴────────────────────┴──────────┴────────────┤
│ 10 rows                                                                                  7 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────
```

</details>


**Pistes :**
> Votre `db/nexamart.duckdb` est absente ou vide ; la requête a été exécutée contre une **base de référence cohorte** (seed instructeur). Les chiffres retournés ne correspondent donc pas à vos propres données : reconstruisez votre base avec `python src/run_pipeline.py` (ou `.\run.ps1 load`) pour valider vos calculs sur votre seed personnel.
> Tables référencées dans votre requête mais absentes de la base : `quarterly_sales`, `with_lag`.
> Tables disponibles dans `db/nexamart.duckdb` : `raw_bridge_campaign_allocation`, `raw_bridge_customer_segment`, `raw_customer_changes`, `raw_customer_profile_bands`, `raw_customer_scd3_history`, `raw_dim_channel`, `raw_dim_customer`, `raw_dim_date`, `raw_dim_geography`, `raw_dim_product`, `raw_dim_segment_outrigger`, `raw_dim_store`, `raw_fact_budget`, `raw_fact_daily_inventory`, `raw_fact_inventory_snapshot`, `raw_fact_order_pipeline`, `raw_fact_orders_transaction`, `raw_fact_promo_exposure`, `raw_fact_returns`, `raw_fact_sales`.

## 2. Rétroaction pédagogique sur le brief

> Bon diagnostic analytique avec requêtes et contrôles solides : les résultats QoQ et les signaux faibles sont bien présentés et accompagnés de recommandations pratiques. Il manque cependant une traçabilité de processus (commits, note IA) et des artefacts de reproduction pour rendre le livrable totalement industriel.

### Observations par dimension

**Model quality**
- Observation : Le brief déclare explicitement le grain «une ligne = une ligne de vente», liste dim_product, dim_store, dim_date et mesure line_total.
- Piste d'amélioration : Justifier le choix de patterns SCD (ex. SCD Type 2 vs Type 1) et explicitement préciser le traitement des attributs qui changent (p. ex. category rename) pour garantir l'historisation.

**Validation quality**
- Observation : La requête SQL fournie calcule les ventes trimestrielles, utilise LAG pour QoQ et le brief inclut réconciliation des totaux et contrôles d'intégrité référentielle (0 orphelins).
- Piste d'amélioration : Ajouter des checks explicites pour les NULLs et un test automatisé (make check) reproduisant la réconciliation afin que le contrôle soit exécutable par un pair.

**Executive justification**
- Observation : La réponse exécutive résume les déclins principaux (ex. Québec/Home & Garden -87% Q2) et propose recommandations court/moyen/long terme actionnables pour le CEO.
- Piste d'amélioration : Synthétiser encore davantage en une phrase de décision claire («Approuvez l'investigation X et la construction du schéma en étoile S02»), et ajouter l'impact business estimé si possible.

**Process trace**
- Observation : Aucune trace de commits git, ni note sur l'usage d'IA ou journal de décisions n'est fournie dans le brief.
- Piste d'amélioration : Inclure un journal de commits (≥3 commits incrémentaux) avec messages et une courte note IA précisant outil, prompt et validation humaine.

**Reproducibility**
- Observation : Le brief contient SQL et tableaux de contrôle, mais il n'y a pas de README/chemins ni script 'make check' explicitement fournis pour exécuter la reproduction sur un clone propre.
- Piste d'amélioration : Ajouter un README pas-à-pas et un script check (ex. make check) sans chemins codés en dur pour permettre à un collègue de reproduire les résultats en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est complète et contient des éléments concrets (outil + version, étapes d'utilisation, validation concrète et limites des données). Rien n'indique l'utilisation d'expressions interdites ; la documentation est suffisamment précise pour l'évaluation.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur `db/nexamart.duckdb` et qu'elle produise la forme attendue (voir pistes en section 1).

---

## 5. Traçabilité

- **Run ID :** `20260514T221333Z-7d34bf6a`
- **Devoir :** `S01`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `8c7e398`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260514T221333Z-7d34bf6a/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
