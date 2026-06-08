-- DRAFT: à réviser par l'instructeur
-- ============================================================
-- dim_customer_scd3 -- SCD Type 3 current/previous (introduite S08)
-- ============================================================
-- Grain : une ligne = un client (unique).
-- Différente de dim_customer (Type 2) : ne conserve que la transition la
-- plus récente du segment, pas tout l'historique.
--
-- Utile pour rapports qui comparent "avant vs maintenant" sans besoin de
-- l'historique complet.
-- ============================================================

CREATE OR REPLACE TABLE dim_customer_scd3 AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    current_segment,
    previous_segment,                            -- NULL si jamais changé
    CAST(segment_change_date AS DATE) AS segment_change_date,
    city,
    province
FROM raw_customer_scd3_history;
