-- ============================================================
-- GRAIN : une ligne = une commande suivie dans son cycle de vie (order_id).
-- Type S09 : Accumulating Snapshot Fact Table.
--   - Dimensions conformes : order_date_key, product_key, store_key, customer_key
--   - Dimension dégénérée : order_id, current_status
-- Jalons : order_date -> payment_date -> pick_date -> ship_date -> delivery_date
-- ============================================================

CREATE OR REPLACE TABLE fact_order_pipeline AS
SELECT
    d.date_key AS order_date_key,
    p.product_key,
    s.store_key,
    c.customer_key,
    o.pipeline_id,
    o.order_id,
    CAST(o.order_date AS DATE) AS order_date,
    CAST(o.payment_date AS DATE) AS payment_date,
    CAST(o.pick_date AS DATE) AS pick_date,
    CAST(o.ship_date AS DATE) AS ship_date,
    CAST(o.delivery_date AS DATE) AS delivery_date,
    o.current_status,
    o.days_order_to_deliver,
    (o.payment_date IS NOT NULL) AS reached_payment,
    (o.pick_date IS NOT NULL) AS reached_pick,
    (o.ship_date IS NOT NULL) AS reached_ship,
    (o.delivery_date IS NOT NULL) AS reached_delivery
FROM raw_fact_order_pipeline AS o
INNER JOIN dim_date AS d
    ON CAST(o.order_date AS DATE) = d."date"
INNER JOIN dim_product AS p
    ON o.product_id = p.product_id
INNER JOIN dim_store AS s
    ON o.store_id = s.store_id
   AND CAST(o.order_date AS DATE) >= s.valid_from
   AND (s.valid_to IS NULL OR CAST(o.order_date AS DATE) < s.valid_to)
INNER JOIN dim_customer AS c
    ON o.customer_id = c.customer_id
   AND CAST(o.order_date AS DATE) >= c.valid_from
   AND (c.valid_to IS NULL OR CAST(o.order_date AS DATE) < c.valid_to);
