-- Retire une ancienne dim_order si elle traînait dans la base (hors modèle S02).
DROP TABLE IF EXISTS dim_order;

-- ============================================================
-- GRAIN : une ligne = une ligne de commande (sale_line_id + order_number).
-- Modèle S02 (lab GIS805-02) + S04 (junk dimension) :
--   - Cinq FK substitut : product_key, customer_key, store_key, date_key, channel_key
--   - FK optionnelle : profile_key → dim_order_profile (drapeaux S04 via raw_orders)
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
    prof.profile_key,
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
   AND CAST(f.order_date AS DATE) >= c.valid_from
   AND (c.valid_to IS NULL OR CAST(f.order_date AS DATE) < c.valid_to)
INNER JOIN dim_product AS p
    ON f.product_id = p.product_id
INNER JOIN dim_store AS s
    ON f.store_id = s.store_id
   AND CAST(f.order_date AS DATE) >= s.valid_from
   AND (s.valid_to IS NULL OR CAST(f.order_date AS DATE) < s.valid_to)
INNER JOIN dim_channel AS ch
    ON f.channel_id = ch.channel_id
INNER JOIN dim_date AS d
    ON f.order_date = d."date"
LEFT JOIN raw_orders AS o
    ON f.order_number = o.order_number
LEFT JOIN dim_order_profile AS prof
    ON  COALESCE(o.is_gift_wrapped, -1) = prof.is_gift_wrapped
    AND COALESCE(o.is_express_shipping, -1) = prof.is_express_shipping
    AND COALESCE(o.is_loyalty_redeemed, -1) = prof.is_loyalty_redeemed
    AND COALESCE(o.is_promo_applied, -1) = prof.is_promo_applied
    AND COALESCE(o.is_employee_purchase, -1) = prof.is_employee_purchase
    AND COALESCE(o.is_online_pickup, -1) = prof.is_online_pickup
    AND COALESCE(o.is_fragile, -1) = prof.is_fragile
    AND COALESCE(o.is_oversized, -1) = prof.is_oversized;
