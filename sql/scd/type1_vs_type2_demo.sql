-- ============================================================
-- S03 — Démonstration SCD Type 1 (trompeur) vs Type 2 (correct)
-- ============================================================
-- Prérequis : make generate && make load
-- Exécution : .\run.ps1 sql sql\scd\type1_vs_type2_demo.sql
-- (Chaque section est autonome ; exécuter bloc par bloc si besoin.)
-- ============================================================

-- ── Bloc 2 : Rapport trompeur (Type 1 — segment courant écrasé) ─────────────
WITH latest_segment_change AS (
    SELECT customer_id, new_value AS segment
    FROM raw_customer_changes
    WHERE change_type = 'segment_change'
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY customer_id ORDER BY change_date DESC
    ) = 1
),
demo_dim_customer_type1 AS (
    SELECT
        c.customer_id,
        COALESCE(lsc.segment, c.loyalty_segment) AS segment
    FROM raw_dim_customer AS c
    LEFT JOIN latest_segment_change AS lsc
        ON c.customer_id = lsc.customer_id
)
SELECT
    'RAPPORT_TYPE1_TROMPEUR' AS demo_step,
    c.segment,
    ROUND(SUM(f.line_total), 2) AS total_revenue,
    COUNT(*) AS line_count
FROM raw_fact_sales AS f
INNER JOIN demo_dim_customer_type1 AS c
    ON f.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_revenue DESC;

-- ── Exemple client CUS-00152 sous Type 1 ───────────────────────────────────
WITH latest_segment_change AS (
    SELECT customer_id, new_value AS segment
    FROM raw_customer_changes
    WHERE change_type = 'segment_change'
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY customer_id ORDER BY change_date DESC
    ) = 1
),
demo_dim_customer_type1 AS (
    SELECT
        c.customer_id,
        COALESCE(lsc.segment, c.loyalty_segment) AS segment
    FROM raw_dim_customer AS c
    LEFT JOIN latest_segment_change AS lsc
        ON c.customer_id = lsc.customer_id
)
SELECT
    'EXEMPLE_CLIENT_TYPE1' AS demo_step,
    c.customer_id,
    c.segment AS segment_affiche,
    ROUND(SUM(f.line_total), 2) AS total_revenue
FROM raw_fact_sales AS f
INNER JOIN demo_dim_customer_type1 AS c
    ON f.customer_id = c.customer_id
WHERE c.customer_id = 'CUS-00152'
GROUP BY c.customer_id, c.segment;

-- ── Bloc 3 : Rapport correct (Type 2 — vérité au moment de la vente) ───────
SELECT
    'RAPPORT_TYPE2_CORRECT' AS demo_step,
    c.segment,
    ROUND(SUM(f.line_total), 2) AS total_revenue,
    COUNT(*) AS line_count
FROM raw_fact_sales AS f
INNER JOIN dim_customer AS c
    ON f.customer_id = c.customer_id
   AND CAST(f.order_date AS DATE) >= c.valid_from
   AND (c.valid_to IS NULL OR CAST(f.order_date AS DATE) < c.valid_to)
GROUP BY c.segment
ORDER BY total_revenue DESC;

-- ── Même client sous Type 2 ─────────────────────────────────────────────────
SELECT
    'EXEMPLE_CLIENT_TYPE2' AS demo_step,
    c.customer_id,
    c.segment AS segment_au_moment_de_la_vente,
    ROUND(SUM(f.line_total), 2) AS total_revenue
FROM raw_fact_sales AS f
INNER JOIN dim_customer AS c
    ON f.customer_id = c.customer_id
   AND CAST(f.order_date AS DATE) >= c.valid_from
   AND (c.valid_to IS NULL OR CAST(f.order_date AS DATE) < c.valid_to)
WHERE c.customer_id = 'CUS-00152'
GROUP BY c.customer_id, c.segment;

-- ── Chaîne historique SCD2 ──────────────────────────────────────────────────
SELECT
    'HISTORIQUE_SCD2' AS demo_step,
    customer_key,
    customer_id,
    segment,
    valid_from,
    valid_to,
    is_current
FROM dim_customer
WHERE customer_id = 'CUS-00152'
ORDER BY valid_from;

-- ── Bloc 4 : Vérifications ──────────────────────────────────────────────────
SELECT
    'CHECK_ONE_CURRENT' AS demo_step,
    CASE WHEN MAX(n_current) = 1 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT COUNT(*) AS n_current
    FROM dim_customer
    WHERE is_current = TRUE
    GROUP BY customer_id
) AS t;

WITH latest_segment_change AS (
    SELECT customer_id, new_value AS segment
    FROM raw_customer_changes
    WHERE change_type = 'segment_change'
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY customer_id ORDER BY change_date DESC
    ) = 1
),
demo_dim_customer_type1 AS (
    SELECT
        c.customer_id,
        COALESCE(lsc.segment, c.loyalty_segment) AS segment
    FROM raw_dim_customer AS c
    LEFT JOIN latest_segment_change AS lsc
        ON c.customer_id = lsc.customer_id
),
gold_t1 AS (
    SELECT ROUND(SUM(f.line_total), 2) AS gold_revenue
    FROM raw_fact_sales AS f
    INNER JOIN demo_dim_customer_type1 AS c
        ON f.customer_id = c.customer_id
    WHERE c.segment = 'Gold'
),
gold_t2 AS (
    SELECT ROUND(SUM(f.line_total), 2) AS gold_revenue
    FROM raw_fact_sales AS f
    INNER JOIN dim_customer AS c
        ON f.customer_id = c.customer_id
       AND CAST(f.order_date AS DATE) >= c.valid_from
       AND (c.valid_to IS NULL OR CAST(f.order_date AS DATE) < c.valid_to)
    WHERE c.segment = 'Gold'
)
SELECT
    'ECART_GOLD' AS demo_step,
    gold_t1.gold_revenue AS gold_type1_trompeur,
    gold_t2.gold_revenue AS gold_type2_correct,
    ROUND(gold_t1.gold_revenue - gold_t2.gold_revenue, 2) AS ecart_dollars
FROM gold_t1, gold_t2;
