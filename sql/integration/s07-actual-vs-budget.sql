-- ============================================================
-- S07 — Réel vs budget
-- Question : où les ventes réelles dépassent-elles ou manquent-elles la cible ?
-- Grain commun : category x store_key x mois.
-- ============================================================

WITH
actual AS (
    SELECT
        p.category,
        f.store_key,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(f.line_total), 2) AS actual_revenue,
        SUM(f.quantity) AS actual_quantity
    FROM fact_sales AS f
    INNER JOIN dim_product AS p
        ON f.product_key = p.product_key
    INNER JOIN dim_date AS d
        ON f.date_key = d.date_key
    GROUP BY
        p.category,
        f.store_key,
        DATE_TRUNC('month', d."date")
),
budget AS (
    SELECT
        category,
        store_key,
        budget_month AS mois,
        ROUND(SUM(target_revenue), 2) AS target_revenue,
        SUM(target_quantity) AS target_quantity
    FROM fact_budget
    GROUP BY
        category,
        store_key,
        budget_month
)
SELECT
    COALESCE(a.category, b.category) AS category,
    s.name AS store_name,
    s."région" AS region,
    COALESCE(a.mois, b.mois) AS mois,
    COALESCE(a.actual_revenue, 0) AS actual_revenue,
    COALESCE(b.target_revenue, 0) AS target_revenue,
    COALESCE(a.actual_revenue, 0) - COALESCE(b.target_revenue, 0) AS variance,
    ROUND(
        100.0
        * (COALESCE(a.actual_revenue, 0) - COALESCE(b.target_revenue, 0))
        / NULLIF(COALESCE(b.target_revenue, 0), 0),
        1
    ) AS pct_variance,
    COALESCE(a.actual_quantity, 0) AS actual_quantity,
    COALESCE(b.target_quantity, 0) AS target_quantity
FROM actual AS a
FULL OUTER JOIN budget AS b
    ON a.category = b.category
   AND a.store_key = b.store_key
   AND a.mois = b.mois
LEFT JOIN dim_store AS s
    ON COALESCE(a.store_key, b.store_key) = s.store_key
ORDER BY
    ABS(variance) DESC,
    category,
    mois;
