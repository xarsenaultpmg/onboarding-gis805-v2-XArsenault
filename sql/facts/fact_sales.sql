-- Retire une ancienne dim_order si elle traînait dans la base (hors modèle S02).
DROP TABLE IF EXISTS dim_order;

-- ============================================================
-- GRAIN : une ligne = une ligne de commande (sale_line_id + order_number).
-- Modèle S02 (lab GIS805-02, docs/s02-sample-brief.md) :
--   - Cinq FK substitut : product_key, customer_key, store_key, date_key, channel_key
--   - Dimension dégénérée : order_number (pas de dim_order)
-- Mesures : revenue, quantity, discount_amount, cost (+ line_total = revenue pour checks)
-- ============================================================

CREATE OR REPLACE TABLE fact_sales AS
SELECT
    p.product_key,
    c.customer_key,
    s.store_key,
    d.date_key,
    ch.channel_key,
    f.sale_line_id,
    f.order_number,
    f.line_total AS revenue,
    f.line_total AS line_total,
    f.quantity,
    f.quantity * f.unit_price * COALESCE(f.discount_pct, 0) AS discount_amount,
    f.quantity * p.unit_cost AS cost
FROM raw_fact_sales AS f
INNER JOIN dim_customer AS c
    ON f.customer_id = c.customer_id
INNER JOIN dim_product AS p
    ON f.product_id = p.product_id
INNER JOIN dim_store AS s
    ON f.store_id = s.store_id
INNER JOIN dim_channel AS ch
    ON f.channel_id = ch.channel_id
INNER JOIN dim_date AS d
    ON f.order_date = d."date";
