-- ============================================================
-- S07 — Drill-across ventes x retours
-- Question : quels taux de retour observe-t-on par catégorie et par mois ?
-- Règle : ne jamais joindre fact_sales et fact_returns directement.
-- Chaque fait est agrégé séparément au grain commun category x mois.
-- ============================================================

WITH
sales_agg AS (
    SELECT
        p.category,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(f.line_total), 2) AS revenue,
        SUM(f.quantity) AS units_sold
    FROM fact_sales AS f
    INNER JOIN dim_product AS p
        ON f.product_key = p.product_key
    INNER JOIN dim_date AS d
        ON f.date_key = d.date_key
    GROUP BY
        p.category,
        DATE_TRUNC('month', d."date")
),
returns_agg AS (
    SELECT
        p.category,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(r.refund_amount), 2) AS total_refunds,
        SUM(r.return_quantity) AS units_returned
    FROM fact_returns AS r
    INNER JOIN dim_product AS p
        ON r.product_key = p.product_key
    INNER JOIN dim_date AS d
        ON r.date_key = d.date_key
    GROUP BY
        p.category,
        DATE_TRUNC('month', d."date")
)
SELECT
    COALESCE(s.category, r.category) AS category,
    COALESCE(s.mois, r.mois) AS mois,
    COALESCE(s.revenue, 0) AS revenue,
    COALESCE(r.total_refunds, 0) AS total_refunds,
    COALESCE(s.revenue, 0) - COALESCE(r.total_refunds, 0) AS net_revenue,
    COALESCE(s.units_sold, 0) AS units_sold,
    COALESCE(r.units_returned, 0) AS units_returned,
    ROUND(
        100.0 * COALESCE(r.total_refunds, 0) / NULLIF(COALESCE(s.revenue, 0), 0),
        2
    ) AS refund_rate_pct
FROM sales_agg AS s
FULL OUTER JOIN returns_agg AS r
    ON s.category = r.category
   AND s.mois = r.mois
ORDER BY
    refund_rate_pct DESC NULLS LAST,
    total_refunds DESC,
    category,
    mois;

-- Vérification à rejouer pendant le sprint :
-- WITH sales_agg AS (...)
-- SELECT SUM(revenue) FROM sales_agg;
-- doit égaler SELECT ROUND(SUM(line_total), 2) FROM fact_sales;
