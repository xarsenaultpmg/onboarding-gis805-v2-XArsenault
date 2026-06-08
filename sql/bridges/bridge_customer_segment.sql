-- DRAFT: à réviser par l'instructeur
-- ============================================================
-- bridge_customer_segment -- pont pondéré M:N (introduite S08)
-- ============================================================
-- GRAIN : une ligne = un client × un segment.
-- Contrainte : SUM(weight) = 1.0 par client (vérifié dans validation/checks.sql).
--
-- Résout la situation M:N : un client peut appartenir à plusieurs segments
-- de fidélité avec des poids différents (ex. 60 % Platinum, 40 % Gold).
-- ============================================================

CREATE OR REPLACE TABLE bridge_customer_segment AS
SELECT
    rb.bridge_id,
    c.customer_key,                               -- FK vers dim_customer (toutes versions SCD2)
    so.segment_key,                                -- FK vers dim_segment_outrigger
    CAST(rb.weight AS DECIMAL(7,4))        AS weight,
    CAST(rb.effective_date AS DATE)        AS effective_date,
    CAST(rb.is_primary AS BOOLEAN)         AS is_primary
FROM raw_bridge_customer_segment rb
JOIN dim_customer c
  ON c.customer_id = rb.customer_id                -- toutes les versions SCD2 pour couvrir les ventes historiques
JOIN dim_segment_outrigger so ON so.segment = rb.segment;

-- Vérification : somme des poids par client = 1.0 (±0.01)
SELECT 'bridge.weight_sum_one' AS check_name,
       CASE WHEN COUNT(*) FILTER (WHERE ABS(total - 1.0) > 0.01) = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT customer_key, SUM(weight) AS total
    FROM bridge_customer_segment
    GROUP BY customer_key
) t;
