-- ============================================================
-- S08 -- Allocation ponderee du revenu par segment
-- ============================================================
-- Source d'analyse : db/nexamart.duckdb apres .\run.ps1 generate/load.
-- Objectif : montrer le fan-out de la jointure naive, puis corriger
-- l'allocation avec bridge_customer_segment.weight.
-- ============================================================

WITH segment_revenue AS (
    SELECT
        seg.segment,
        SUM(f.line_total) AS revenue_naive,
        SUM(CASE WHEN b.is_primary THEN f.line_total ELSE 0 END) AS revenue_primary,
        SUM(f.line_total * b.weight) AS revenue_weighted
    FROM fact_sales AS f
    JOIN bridge_customer_segment AS b
      ON b.customer_key = f.customer_key
    JOIN dim_segment_outrigger AS seg
      ON seg.segment_key = b.segment_key
    GROUP BY seg.segment
),
total_sales AS (
    SELECT SUM(line_total) AS total_revenue
    FROM fact_sales
),
campaign_spend AS (
    -- planned_spend is already allocated per campaign x segment row in S08.
    SELECT
        segment,
        SUM(planned_spend) AS allocated_spend
    FROM raw_bridge_campaign_allocation
    GROUP BY segment
)
SELECT
    sr.segment,
    ROUND(sr.revenue_naive, 2) AS revenue_naive,
    ROUND(sr.revenue_primary, 2) AS revenue_primary,
    ROUND(sr.revenue_weighted, 2) AS revenue_weighted,
    ROUND(COALESCE(cs.allocated_spend, 0), 2) AS campaign_allocated_spend,
    ROUND(sr.revenue_naive - sr.revenue_weighted, 2) AS naive_overstatement,
    ROUND(sr.revenue_naive / NULLIF(sr.revenue_weighted, 0), 4) AS naive_to_weighted_ratio,
    ROUND(sr.revenue_weighted / NULLIF(ts.total_revenue, 0), 4) AS weighted_share_of_total
FROM segment_revenue AS sr
CROSS JOIN total_sales AS ts
LEFT JOIN campaign_spend AS cs
  ON cs.segment = sr.segment
ORDER BY sr.revenue_weighted DESC;
