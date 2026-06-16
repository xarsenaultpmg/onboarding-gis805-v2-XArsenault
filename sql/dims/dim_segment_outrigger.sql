-- ============================================================
-- dim_segment_outrigger -- attributs descriptifs des segments S08
-- ============================================================
-- GRAIN : une ligne = un segment client.
-- Source : raw_dim_segment_outrigger generee par le seed local.
-- Cette dimension fournit la cle segment_key utilisee par le pont
-- bridge_customer_segment.
-- ============================================================

CREATE OR REPLACE TABLE dim_segment_outrigger AS
SELECT
    ROW_NUMBER() OVER (ORDER BY segment)::BIGINT AS segment_key,
    segment,
    CAST(discount_pct AS DECIMAL(5,2)) AS discount_pct,
    CAST(free_shipping AS BOOLEAN) AS free_shipping,
    CAST(priority_support AS BOOLEAN) AS priority_support,
    CAST(annual_reward_value AS DECIMAL(10,2)) AS annual_reward_value
FROM raw_dim_segment_outrigger
WHERE segment IS NOT NULL;
