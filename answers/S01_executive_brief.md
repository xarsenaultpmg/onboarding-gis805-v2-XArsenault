# Board Brief — S01

## Question du CEO

**Quelles catégories déclinent dans quelles régions et pourquoi ? Chaque étudiant doit identifier sa première question exécutive.**

## Réponse exécutive

Les données de ventes couvrent l'année 2025 et contiennent les transactions ligne par ligne. Cependant, fact_sales ne stocke que des identifiants (product_id, store_id) — les catégories de produits et les régions géographiques sont dans des tables séparées (dim_produit, dim_store). Sans jointure explicite entre ces tables, il est impossible de répondre directement à la question du CEO ce soir.

En 2025, l'analyse trimestrielle révèle des déclins significatifs dans plusieurs combinaisons région/catégorie. Les baisses les plus sévères en pourcentage sont Québec/Home & Garden (-87% en Q2), Estrie/Clothing (-85% en Q2) et BC/Books & Media (-84% en Q3). En valeur absolue, Alberta/Automotive représente la perte la plus importante (-4 935 $ en Q4) suivi de Ouaouais/Pet Supplies (-3 009 $ en Q3).
Ces déclins sont mesurés par rapport au trimestre précédent. L'amplitude des baisses — certaines dépassant 80% — suggère que la saisonnalité seule ne suffit pas à expliquer ces chutes, et qu'un problème structurel pourrait être en cause dans ces régions et catégories.

## Décisions de modélisation

Mesure : line_total (revenu net par ligne de vente)
Dimension produit : category dans dim_produit, lié via product_id
Dimension géographie : region dans dim_store, lié via store_id
Dimension temps : order_date dans fact_sales — à découper en trimestres via dim_date
Grain : une ligne = une ligne de vente (un produit dans une commande)

## Preuve

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

## Validation

**1. Réconciliation des totaux**

| | Valeur |
|---|---|
| SUM(line_total) brut | 896 840.55 $ |
| SUM(line_total) avec jointures | 896 840.55 $ |
| Écart | 0.00 $ |

**2. Intégrité référentielle**

| Dimension | Orphelins |
|---|---|
| raw_dim_product | 0 |
| raw_dim_store | 0 |
| raw_dim_date | 0 |

**3. Grain**

| Total lignes | IDs uniques | Grain OK |
|---|---|---|
| 3 670 | 3 670 | ✓ |

**Note business** : Québec/Home & Garden affiche le déclin le plus fort en pourcentage (-87% en Q2), mais ce trimestre ne compte que 5 transactions contre 25 en Q1. Ce signal est statistiquement fragile et ne devrait pas être interprété comme un déclin structurel. Les analyses futures devront établir un seuil minimum de transactions avant de signaler un déclin au CEO.

## Risques / limites

- **Données limitées à 2025** : `raw_fact_sales` ne couvre qu'une seule année — une comparaison année sur année est impossible. L'analyse de tendance est limitée à la comparaison entre trimestres consécutifs.

- **Risque de confusion saisonnalité / déclin structurel** : sans données historiques (2024 et avant), il est impossible de distinguer un déclin réel d'une variation saisonnière normale.

- **Faible volume de transactions** : certains déclins en pourcentage (ex. Québec/Home & Garden, -87% en Q2) reposent sur 5 transactions seulement — ces signaux sont fragiles et pourraient être du bruit statistique.

- **Absence de seuil minimal** : aucun seuil de volume n'a été défini pour qualifier un déclin comme significatif. Une combinaison région/catégorie avec 3 transactions ne devrait pas être comparée à une avec 50.

- **Comparaison QoQ uniquement** : la window function `LAG` compare chaque trimestre au précédent dans la même année — Q1 n'a pas de trimestre précédent et est donc exclu de l'analyse.

## Prochaine recommandation

## Prochaine recommandation

- **Court terme** : Valider les déclins identifiés en croisant avec `raw_fact_returns` et `raw_fact_inventory_snapshot` pour distinguer une baisse de demande réelle d'un problème opérationnel (rupture de stock, taux de retour élevé).

- **Moyen terme** : Construire un schéma en étoile (S02) avec `raw_fact_sales` au centre, relié aux dimensions `raw_dim_product`, `raw_dim_store` et `raw_dim_date` — ce qui rendra l'analyse reproductible, auditable et partageable.

- **Long terme** : Intégrer les données de 2024 pour permettre une comparaison année sur année et distinguer les tendances structurelles des variations saisonnières.