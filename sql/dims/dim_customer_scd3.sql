-- ============================================================
-- dim_customer_scd3 -- segment actuel vs segment precedent (S08)
-- ============================================================
-- GRAIN : une ligne = un client courant.
-- SCD Type 3 : current_segment et previous_segment cohabitent dans
-- la meme ligne pour analyser les transitions recentes sans historique
-- complet.
-- ============================================================

CREATE OR REPLACE TABLE dim_customer_scd3 AS
SELECT
    c.customer_key,
    c.customer_id,
    c.name,
    h.current_segment,
    h.previous_segment,
    CAST(h.segment_change_date AS DATE) AS segment_change_date,
    h.city,
    h.province
FROM dim_customer AS c
JOIN raw_customer_scd3_history AS h
  ON h.customer_id = c.customer_id
WHERE c.is_current = TRUE;
