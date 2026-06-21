# Définitions de métriques — NexaMart

> **Minimum 4 KPIs couvrant au moins 2 tables de faits différentes.**
> Ce document complète le handoff pack : il traduit les requêtes SQL en KPIs
> compréhensibles par le CEO.
>
> Chaque formule a été **testée sur `db/nexamart.duckdb`** (seed local
> `xarsenaultpmg`) le 2026-06-18, après retour de revue par les pairs S10.

## Format d'une entrée

| Champ | Contenu attendu |
|---|---|
| **Nom** | Nom court utilisable dans un tableau de bord |
| **Définition business** | Ce que le CEO peut décider avec ce chiffre — sans jargon SQL |
| **Formule SQL** | Requête exécutable, grain explicite, alias de colonnes clairs |
| **Source** | Tables interrogées (`fact_*`, `dim_*`) |
| **Fréquence** | À quelle fréquence ce KPI est recalculé en production |

---

## KPIs officiels

| Nom | Définition business | Formule SQL (grain explicite) | Source | Fréquence |
|---|---|---|---|---|
| **Revenu net mensuel** | Montant total facturé aux clients en CAD par mois, **avant déduction des retours** (les remboursements sont couverts par le KPI « taux de retour ») — base de décision pricing et performance | `SELECT DATE_TRUNC('month', d."date") AS mois, ROUND(SUM(s.line_total), 2) AS net_revenue FROM fact_sales AS s JOIN dim_date AS d ON d.date_key = s.date_key GROUP BY 1 ORDER BY 1` | `fact_sales`, `dim_date` | Mensuel |
| **Taux de livraison pipeline** | Part des commandes suivies qui ont atteint le jalon livraison — mesure l'efficacité opérationnelle entrepôt | `SELECT ROUND(100.0 * COUNT(delivery_date) / NULLIF(COUNT(*), 0), 1) AS pct_delivery FROM fact_order_pipeline` | `fact_order_pipeline` | Quotidien |
| **Taux de retour par catégorie et mois** | Part du revenu remboursée par catégorie et par mois — signale qualité produit ou problème logistique sans joindre ventes et retours ligne à ligne | Voir requête complète ci-dessous (`refund_rate_pct`) | `fact_sales`, `fact_returns`, `dim_product`, `dim_date` | Mensuel |
| **Couverture promo clients actifs** | Part des clients courants exposés à au moins une campagne — mesure la portée marketing sans confondre exposition et achat | `SELECT ROUND(100.0 * COUNT(DISTINCT e.customer_key) / NULLIF((SELECT COUNT(*) FROM dim_customer WHERE is_current = TRUE), 0), 1) AS pct_clients_actifs_exposes FROM fact_promo_exposure AS e` | `fact_promo_exposure`, `dim_customer` | Hebdomadaire |
| **Écart réel vs budget** | Écart en % entre revenu réel et cible budgétaire — signale les catégories et magasins qui manquent ou dépassent la cible finance | Voir requête complète ci-dessous (`pct_variance`) | `fact_sales`, `fact_budget`, `dim_product`, `dim_date`, `dim_store` | Mensuel |

### Détail — Écart réel vs budget

Grain commun : **catégorie × magasin × mois** (voir `sql/integration/s07-actual-vs-budget.sql`).

```sql
WITH actual AS (
    SELECT
        p.category,
        f.store_key,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(f.line_total), 2) AS actual_revenue
    FROM fact_sales AS f
    INNER JOIN dim_product AS p ON f.product_key = p.product_key
    INNER JOIN dim_date AS d ON f.date_key = d.date_key
    GROUP BY 1, 2, 3
),
budget AS (
    SELECT
        category,
        store_key,
        budget_month AS mois,
        ROUND(SUM(target_revenue), 2) AS target_revenue
    FROM fact_budget
    GROUP BY 1, 2, 3
)
SELECT
    COALESCE(a.category, b.category) AS category,
    COALESCE(a.mois, b.mois) AS mois,
    COALESCE(a.actual_revenue, 0) AS actual_revenue,
    COALESCE(b.target_revenue, 0) AS target_revenue,
    ROUND(
        100.0 * (COALESCE(a.actual_revenue, 0) - COALESCE(b.target_revenue, 0))
        / NULLIF(COALESCE(b.target_revenue, 0), 0),
        1
    ) AS pct_variance
FROM actual AS a
FULL OUTER JOIN budget AS b
    ON a.category = b.category
   AND a.store_key = b.store_key
   AND a.mois = b.mois
WHERE COALESCE(b.target_revenue, 0) > 0
ORDER BY ABS(COALESCE(a.actual_revenue, 0) - COALESCE(b.target_revenue, 0)) DESC;
```

### Détail — Taux de retour par catégorie et mois

Grain commun : **catégorie × mois**. Chaque fait est agrégé séparément avant jointure
(voir `sql/integration/s07-drill-across.sql`).

```sql
WITH sales_agg AS (
    SELECT
        p.category,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(f.line_total), 2) AS revenue
    FROM fact_sales AS f
    INNER JOIN dim_product AS p ON f.product_key = p.product_key
    INNER JOIN dim_date AS d ON f.date_key = d.date_key
    GROUP BY 1, 2
),
returns_agg AS (
    SELECT
        p.category,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(r.refund_amount), 2) AS total_refunds
    FROM fact_returns AS r
    INNER JOIN dim_product AS p ON r.product_key = p.product_key
    INNER JOIN dim_date AS d ON r.date_key = d.date_key
    GROUP BY 1, 2
)
SELECT
    COALESCE(s.category, r.category) AS category,
    COALESCE(s.mois, r.mois) AS mois,
    COALESCE(s.revenue, 0) AS revenue,
    COALESCE(r.total_refunds, 0) AS total_refunds,
    ROUND(
        100.0 * COALESCE(r.total_refunds, 0) / NULLIF(COALESCE(s.revenue, 0), 0),
        2
    ) AS refund_rate_pct
FROM sales_agg AS s
FULL OUTER JOIN returns_agg AS r
    ON s.category = r.category AND s.mois = r.mois
WHERE COALESCE(s.revenue, 0) > 0
ORDER BY refund_rate_pct DESC NULLS LAST;
```

---

## Valeurs observées (seed `xarsenaultpmg`, 2026-06-18)

| KPI | Valeur observée sur DuckDB | Testé ? |
|---|---|---|
| Revenu net mensuel | `2025-01 : 62 630,86 $` ; `2025-12 : 54 228,47 $` | [x] |
| Taux de livraison pipeline | `70,2 %` | [x] |
| Taux de retour par catégorie et mois | `Automotive / 2025-03 : 21,42 %` (pic observé) | [x] |
| Couverture promo clients actifs | `46,3 %` (132 clients exposés sur clients courants) | [x] |
| Écart réel vs budget | `Sports & Outdoors / 2025-05 : -99,3 %` (plus grand écart absolu observé) | [x] |

---

## Règles de qualité

1. **Grain explicite** — la formule doit indiquer le niveau d'agrégation. `SUM(revenue)` seul n'est pas un KPI livrable. `SUM(revenue) GROUP BY dim_date.month` l'est.
2. **Alias clairs** — chaque colonne de résultat doit avoir un alias lisible (`AS net_revenue`, pas `AS col1`).
3. **NULLs traités** — utilisez `NULLIF(COUNT(*), 0)` pour éviter la division par zéro. Les dates NULL du pipeline signifient « jalon non atteint », pas erreur de chargement.
4. **Au moins 2 tables de faits différentes** — les 5 KPIs ci-dessus couvrent `fact_sales`, `fact_returns`, `fact_budget`, `fact_order_pipeline` et `fact_promo_exposure`.
5. **Références croisées** — voir aussi `docs/model-card.md` (grains et additivité), `docs/bus-matrix.md` (grains communs) et `docs/decision-log.md` (D05 drill-across, D07 types de faits).

---

## KPI complémentaire (segment pondéré)

Non requis pour la remise S11, mais utile pour le board S08 :

```sql
SELECT
    seg.segment,
    ROUND(SUM(f.line_total * b.weight), 2) AS revenue_weighted
FROM fact_sales AS f
JOIN bridge_customer_segment AS b ON b.customer_key = f.customer_key
JOIN dim_segment_outrigger AS seg ON seg.segment_key = b.segment_key
GROUP BY 1
ORDER BY revenue_weighted DESC;
```

Valeur observée : segment `Platinum` = `136 376,28 $` (attribution pondérée, réconciliable au total ventes).
