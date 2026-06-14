-- ============================================================
-- GRAIN : une ligne = un produit x un magasin x une date de snapshot.
-- Type S09 : Periodic Snapshot Fact Table.
--   - Dimensions conformes : date_key, product_key, store_key
-- Mesures semi-additives : quantity_on_hand, quantity_on_order, days_of_supply
-- ============================================================

CREATE OR REPLACE TABLE fact_daily_inventory AS
SELECT
    d.date_key,
    p.product_key,
    s.store_key,
    i.snapshot_id,
    CAST(i.snapshot_date AS DATE) AS snapshot_date,
    i.quantity_on_hand,
    i.quantity_on_order,
    i.days_of_supply
FROM raw_fact_daily_inventory AS i
INNER JOIN dim_date AS d
    ON CAST(i.snapshot_date AS DATE) = d."date"
INNER JOIN dim_product AS p
    ON i.product_id = p.product_id
INNER JOIN dim_store AS s
    ON i.store_id = s.store_id
   AND CAST(i.snapshot_date AS DATE) >= s.valid_from
   AND (s.valid_to IS NULL OR CAST(i.snapshot_date AS DATE) < s.valid_to);
