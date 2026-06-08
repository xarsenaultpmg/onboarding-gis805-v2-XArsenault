-- DRAFT: à réviser par l'instructeur
-- ============================================================
-- dim_segment_outrigger -- outrigger dimension (introduite S08)
-- ============================================================
-- Grain : une ligne = un segment de fidélité.
-- Utilisée par les ponts customer-segment et campaign-allocation.
-- ============================================================

CREATE OR REPLACE TABLE dim_segment_outrigger AS
SELECT
    ROW_NUMBER() OVER (ORDER BY segment) AS segment_key,
    segment,
    CAST(discount_pct AS DECIMAL(5,2))   AS discount_pct,
    CAST(free_shipping AS BOOLEAN)       AS free_shipping,
    CAST(priority_support AS BOOLEAN)    AS priority_support,
    CAST(annual_reward_value AS DECIMAL(10,2)) AS annual_reward_value
FROM raw_dim_segment_outrigger;
