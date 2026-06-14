-- ============================================================
-- GRAIN : une ligne = une transaction atomique (transaction_id).
-- Type S09 : Transaction Fact Table.
--   - Dimensions conformes : date_key, product_key, store_key, customer_key
--   - Dimension dégénérée : transaction_id, transaction_type
-- Mesures additives : quantity, amount
-- ============================================================

CREATE OR REPLACE TABLE fact_orders_transaction AS
SELECT
    d.date_key,
    p.product_key,
    s.store_key,
    c.customer_key,
    t.transaction_id,
    CAST(t.transaction_date AS DATE) AS transaction_date,
    t.transaction_type,
    t.quantity,
    t.amount
FROM raw_fact_orders_transaction AS t
INNER JOIN dim_date AS d
    ON CAST(t.transaction_date AS DATE) = d."date"
INNER JOIN dim_product AS p
    ON t.product_id = p.product_id
INNER JOIN dim_store AS s
    ON t.store_id = s.store_id
   AND CAST(t.transaction_date AS DATE) >= s.valid_from
   AND (s.valid_to IS NULL OR CAST(t.transaction_date AS DATE) < s.valid_to)
INNER JOIN dim_customer AS c
    ON t.customer_id = c.customer_id
   AND CAST(t.transaction_date AS DATE) >= c.valid_from
   AND (c.valid_to IS NULL OR CAST(t.transaction_date AS DATE) < c.valid_to);
