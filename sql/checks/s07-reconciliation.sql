-- ============================================================
-- S07 — Réconciliation drill-across
-- But : vérifier que les CTEs agrégées conservent les totaux directs.
-- Les écarts doivent être 0.00.
-- ============================================================

WITH
sales_agg AS (
    SELECT
        p.category,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(f.line_total), 2) AS revenue
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
        ROUND(SUM(r.refund_amount), 2) AS refunds
    FROM fact_returns AS r
    INNER JOIN dim_product AS p
        ON r.product_key = p.product_key
    INNER JOIN dim_date AS d
        ON r.date_key = d.date_key
    GROUP BY
        p.category,
        DATE_TRUNC('month', d."date")
),
actual AS (
    SELECT
        p.category,
        f.store_key,
        DATE_TRUNC('month', d."date") AS mois,
        ROUND(SUM(f.line_total), 2) AS actual_revenue
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
        ROUND(SUM(target_revenue), 2) AS target_revenue
    FROM fact_budget
    GROUP BY
        category,
        store_key,
        budget_month
),
checks AS (
    SELECT
        'sales direct vs drill_across' AS check_name,
        ROUND((SELECT SUM(line_total) FROM fact_sales), 2) AS direct_total,
        ROUND((SELECT SUM(revenue) FROM sales_agg), 2) AS agg_total
    UNION ALL
    SELECT
        'returns direct vs drill_across' AS check_name,
        ROUND((SELECT SUM(refund_amount) FROM fact_returns), 2) AS direct_total,
        ROUND((SELECT SUM(refunds) FROM returns_agg), 2) AS agg_total
    UNION ALL
    SELECT
        'sales direct vs actual_budget_actual' AS check_name,
        ROUND((SELECT SUM(line_total) FROM fact_sales), 2) AS direct_total,
        ROUND((SELECT SUM(actual_revenue) FROM actual), 2) AS agg_total
    UNION ALL
    SELECT
        'budget direct vs actual_budget_budget' AS check_name,
        ROUND((SELECT SUM(target_revenue) FROM fact_budget), 2) AS direct_total,
        ROUND((SELECT SUM(target_revenue) FROM budget), 2) AS agg_total
)
SELECT
    check_name,
    direct_total,
    agg_total,
    ROUND(direct_total - agg_total, 2) AS difference,
    CASE
        WHEN ROUND(direct_total - agg_total, 2) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS result
FROM checks;
