-- ============================================================
-- S08 -- Reconciliation du pont pondere
-- ============================================================
-- Source d'analyse : db/nexamart.duckdb apres .\run.ps1 generate/load.
-- Ces controles prouvent que l'allocation par bridge_customer_segment
-- conserve le total reel des ventes.
-- ============================================================

WITH true_total AS (
    SELECT SUM(line_total) AS total_revenue
    FROM fact_sales
),
naive_total AS (
    SELECT SUM(f.line_total) AS total_revenue
    FROM fact_sales AS f
    JOIN bridge_customer_segment AS b
      ON b.customer_key = f.customer_key
),
weighted_total AS (
    SELECT SUM(f.line_total * b.weight) AS total_revenue
    FROM fact_sales AS f
    JOIN bridge_customer_segment AS b
      ON b.customer_key = f.customer_key
),
weight_violations AS (
    SELECT COUNT(*) AS nb_customers
    FROM (
        SELECT customer_key, SUM(weight) AS total_weight
        FROM bridge_customer_segment
        GROUP BY customer_key
        HAVING ABS(SUM(weight) - 1.0) > 0.01
    ) AS bad_weights
),
campaign_weight_violations AS (
    SELECT COUNT(*) AS nb_campaigns
    FROM (
        SELECT campaign_id, SUM(budget_weight) AS total_weight
        FROM raw_bridge_campaign_allocation
        GROUP BY campaign_id
        HAVING ABS(SUM(budget_weight) - 1.0) > 0.01
    ) AS bad_weights
),
campaign_allocated AS (
    -- planned_spend is already the allocated spend per campaign x segment row
    -- in the generated S08 data, so it must not be multiplied a second time.
    SELECT SUM(planned_spend) AS total_allocated_spend
    FROM raw_bridge_campaign_allocation
)
SELECT
    'bridge_weight_sum' AS check_name,
    CAST(wv.nb_customers AS DOUBLE) AS reference_value,
    0.00 AS compared_value,
    CAST(wv.nb_customers AS DOUBLE) AS difference,
    CASE WHEN wv.nb_customers = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM weight_violations AS wv

UNION ALL

SELECT
    'sales_total_weighted_vs_real' AS check_name,
    ROUND(tt.total_revenue, 2) AS reference_value,
    ROUND(wt.total_revenue, 2) AS compared_value,
    ROUND(wt.total_revenue - tt.total_revenue, 2) AS difference,
    CASE WHEN ABS(wt.total_revenue - tt.total_revenue) <= 0.01 THEN 'PASS' ELSE 'FAIL' END AS result
FROM true_total AS tt
CROSS JOIN weighted_total AS wt

UNION ALL

SELECT
    'naive_fanout_observed' AS check_name,
    ROUND(tt.total_revenue, 2) AS reference_value,
    ROUND(nt.total_revenue, 2) AS compared_value,
    ROUND(nt.total_revenue - tt.total_revenue, 2) AS difference,
    CASE WHEN nt.total_revenue > tt.total_revenue THEN 'INFO' ELSE 'CHECK' END AS result
FROM true_total AS tt
CROSS JOIN naive_total AS nt

UNION ALL

SELECT
    'campaign_budget_weight_sum' AS check_name,
    CAST(cwv.nb_campaigns AS DOUBLE) AS reference_value,
    0.00 AS compared_value,
    CAST(cwv.nb_campaigns AS DOUBLE) AS difference,
    CASE WHEN cwv.nb_campaigns = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM campaign_weight_violations AS cwv

UNION ALL

SELECT
    'campaign_allocated_spend' AS check_name,
    ROUND(ca.total_allocated_spend, 2) AS reference_value,
    ROUND(ca.total_allocated_spend, 2) AS compared_value,
    0.00 AS difference,
    'INFO' AS result
FROM campaign_allocated AS ca;
