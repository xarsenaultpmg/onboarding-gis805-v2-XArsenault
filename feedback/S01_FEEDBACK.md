# Rétroaction automatisée -- S01 (Diagnostic fondamental -- NexaMart kickoff)

_Générée le 2026-05-15T12:36:02+00:00 -- Run `20260515T122624Z-00a5a04f`_

Ce document est produit par un pipeline reproductible (vérification SQL déterministe + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

> ⚠️ **Avertissement instructeur (à retirer avant publication) :** cette analyse a été générée avec `--skip-pull`. Le contenu correspond au commit local et **n'est peut-être pas la dernière version poussée par l'étudiant·e**.

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
> Tables référencées dans votre requête mais absentes de la base : `quarterly_sales`, `with_lag`.
> Tables disponibles dans `db/nexamart.duckdb` : `raw_bridge_campaign_allocation`, `raw_bridge_customer_segment`, `raw_customer_changes`, `raw_customer_profile_bands`, `raw_customer_scd3_history`, `raw_dim_channel`, `raw_dim_customer`, `raw_dim_date`, `raw_dim_geography`, `raw_dim_product`, `raw_dim_segment_outrigger`, `raw_dim_store`, `raw_fact_budget`, `raw_fact_daily_inventory`, `raw_fact_inventory_snapshot`, `raw_fact_order_pipeline`, `raw_fact_orders_transaction`, `raw_fact_promo_exposure`, `raw_fact_returns`, `raw_fact_sales`.

## 2. Rétroaction pédagogique sur le brief

> Très bon diagnostic : le modèle, les requêtes et les contrôles sont complets et la justification exécutive est pertinente. Il manque toutefois la traçabilité du processus (commits, note IA) et des instructions explicites de reproduction pour un coéquipier.

### Observations par dimension

**Model quality**
- Observation : Le brief précise le grain (« une ligne = une ligne de vente »), définit les dimensions (category via dim_produit, region via dim_store, dim_date) et propose la mesure line_total comme 'revenu net par ligne de vente'.
- Piste d'amélioration : Ajouter une discussion explicite sur la stratégie SCD (type 2 vs type 1) et justifier le pattern choisi pour préserver l'historique des catégories.

**Validation quality**
- Observation : Le livrable inclut une requête SQL reproduisible qui calcule les ventes trimestrielles, l'usage de LAG pour QoQ, et des contrôles de réconciliation et d'intégrité référentielle (écart 0 $, orphelins 0).
- Piste d'amélioration : Documenter le traitement des cas limites dans la requête (p.ex. prev_quarter_sales = 0, NULLs) et ajouter un check automatisé 'make check' listé dans le README.

**Executive justification**
- Observation : La section 'Réponse exécutive' résume les déclins clés (ex. Québec/Home & Garden -87% Q2) et conclut que certains signaux sont statistiquement fragiles, avec recommandations opérationnelles et priorités court/moyen/long terme.
- Piste d'amélioration : Formuler une décision claire à demander au CEO (p.ex. valider investigation prioritaire pour les 3 combinaisons région/catégorie listées) et préciser le seuil décisionnel utilisé.

**Process trace**
- Observation : Le brief ne contient aucune trace de commits git, ni note sur l'usage d'IA ou journal de décisions.
- Piste d'amélioration : Inclure un bref historique de commits (≥3) avec messages, et une note IA indiquant outils utilisés + validation humaine.

**Reproducibility**
- Observation : Le SQL et les résultats sont fournis dans le brief, mais il manque des instructions de reproduction (README, commandes DuckDB/Make, ou chemins relatifs).
- Piste d'amélioration : Ajouter un README minimal avec étapes 'clone → ouvrir DuckDB / run sql → make check' et exemples de commandes pour reproduire les checks en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est complète et documente l'outil (avec version), le rôle joué par l'IA, les vérifications humaines et des limites de données. Bon niveau de détail; continuez d'être aussi précis pour les prochaines séances.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur `db/nexamart.duckdb` et qu'elle produise la forme attendue (voir pistes en section 1).

---

## 5. Traçabilité

- **Run ID :** `20260515T122624Z-00a5a04f`
- **Devoir :** `S01`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `d6c610c`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260515T122624Z-00a5a04f/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
