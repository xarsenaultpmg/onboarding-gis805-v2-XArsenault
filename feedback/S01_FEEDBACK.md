# Rétroaction automatisée -- S01 (Diagnostic fondamental -- NexaMart kickoff)

_Générée le 2026-05-14T20:11:37+00:00 -- Run `20260514T200711Z-2707a635`_

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

> Bon diagnostic et preuves SQL convaincantes avec réconciliations et recommandations opérationnelles claires. Il manque toutefois la traçabilité (commits/note IA) et des artefacts de reproductibilité (README/make check) pour productionnaliser le livrable.

### Observations par dimension

**Model quality**
- Observation : Le brief indique un grain clair («une ligne = une ligne de vente»), décrit dim_product/dim_store/dim_date et fournit le SQL de regroupement par catégorie, région et trimestre.
- Piste d'amélioration : Mentionner explicitement la stratégie SCD (ex. SCD Type 2) et les attributs historisés, et noter les attributs non-additifs (unit_price) pour éviter des erreurs analytiques.

**Validation quality**
- Observation : Le livrable inclut une requête de validation complète (aggregation + LAG) et des contrôles : réconciliation SUM(line_total) = 0 écart, intégrité référentielle 0 orphelins et vérification du grain.
- Piste d'amélioration : Ajouter des contrôles sur les NULLs et des tests de robustesse (seuil minimal de transactions, divisions par zéro protégées) et documenter les résultats de ces checks dans un script exécutable (make check).

**Executive justification**
- Observation : La section 'Réponse exécutive' présente des déclins chiffrés par région/catégorie, interprète la fiabilité statistique et propose des recommandations court/moyen/long terme destinées au CEO.
- Piste d'amélioration : Formuler en une phrase-action claire en tête (ex. «Décision demandée : autoriser la vérification opérationnelle et importer 2024»), pour faciliter la prise de décision du board.

**Process trace**
- Observation : Le brief ne documente ni historique de commits git ni note d'usage d'IA ou decision log.
- Piste d'amélioration : Inclure un lien vers le repo avec au moins 3 commits décrivant étapes, et une note IA précisant outil+usage+validation humaine dans le README ou le decision log.

**Reproducibility**
- Observation : Le SQL et les contrôles sont fournis, mais il n'y a pas de README ou d'instructions d'exécution (chemins, dépendances, comment lancer les checks).
- Piste d'amélioration : Ajouter un README/makefile expliquant comment cloner, charger les fichiers raw_, exécuter la requête de validation et obtenir les mêmes tableaux (DuckDB + commandes make check).

## 3. Déclaration d'utilisation de l'IA

> La déclaration est précise et documente l'outil (nom + version), le contexte d'utilisation, la validation humaine et une limite de données pertinente. Bon niveau de détail — conserve ce format pour les prochaines remises.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur `db/nexamart.duckdb` et qu'elle produise la forme attendue (voir pistes en section 1).

---

## 5. Traçabilité

- **Run ID :** `20260514T200711Z-2707a635`
- **Devoir :** `S01`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `e95199d`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260514T200711Z-2707a635/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
  - `sql_extractor_system` : `90ee9e277de7a27f...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
