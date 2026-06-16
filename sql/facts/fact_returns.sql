-- ============================================================
-- GRAIN : une ligne = une ligne de retour.
-- Modèle S07 : table de faits conforme à fact_sales pour drill-across.
--   - Dimensions conformes : product_key, customer_key, store_key, date_key, channel_key
--   - Dimension dégénérée : original_sale_line_id
-- Mesures : refund_amount, return_quantity
-- ============================================================

CREATE OR REPLACE TABLE fact_returns AS
SELECT
    p.product_key,
    c.customer_key,
    s.store_key,
    d.date_key,
    ch.channel_key,
    r.return_id,
    r.original_sale_line_id,
    CAST(r.return_date AS DATE) AS return_date,
    r.return_reason,
    r.return_quantity,
    r.refund_amount
FROM raw_fact_returns AS r
INNER JOIN raw_fact_sales AS sale
    ON r.original_sale_line_id = sale.sale_line_id
INNER JOIN dim_product AS p
    ON r.product_id = p.product_id
INNER JOIN dim_customer AS c
    ON sale.customer_id = c.customer_id
   AND CAST(sale.order_date AS DATE) >= c.valid_from
   AND (c.valid_to IS NULL OR CAST(sale.order_date AS DATE) < c.valid_to)
INNER JOIN dim_store AS s
    ON r.store_id = s.store_id
   AND CAST(r.return_date AS DATE) >= s.valid_from
   AND (s.valid_to IS NULL OR CAST(r.return_date AS DATE) < s.valid_to)
INNER JOIN dim_channel AS ch
    ON sale.channel_id = ch.channel_id
INNER JOIN dim_date AS d
    ON CAST(r.return_date AS DATE) = d."date";
