-- ============================================================
-- GRAIN : une ligne = un produit x un magasin x une date de snapshot.
-- Modèle S07 : inventaire intégré via dimensions conformes.
--   - Dimensions conformes : date_key, product_key, store_key
-- Mesures semi-additives : quantity_on_hand, quantity_on_order, reorder_point
-- ============================================================

CREATE OR REPLACE TABLE fact_inventory_snapshot AS
SELECT
    d.date_key,
    p.product_key,
    s.store_key,
    inv.snapshot_id,
    CAST(inv.snapshot_date AS DATE) AS snapshot_date,
    inv.quantity_on_hand,
    inv.quantity_on_order,
    inv.reorder_point
FROM raw_fact_inventory_snapshot AS inv
INNER JOIN dim_date AS d
    ON CAST(inv.snapshot_date AS DATE) = d."date"
INNER JOIN dim_product AS p
    ON inv.product_id = p.product_id
INNER JOIN dim_store AS s
    ON inv.store_id = s.store_id
   AND CAST(inv.snapshot_date AS DATE) >= s.valid_from
   AND (s.valid_to IS NULL OR CAST(inv.snapshot_date AS DATE) < s.valid_to);
