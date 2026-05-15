-- Dimension produit (diapo NexaMart) : product_key, name, category, subcategory, brand.
-- Source : raw_dim_product. unit_cost / unit_price conservés pour le calcul du coût au fait.

CREATE OR REPLACE TABLE dim_product AS
SELECT
    ROW_NUMBER() OVER (ORDER BY product_id)::BIGINT AS product_key,
    product_id,
    product_name AS name,
    category,
    subcategory,
    brand,
    unit_cost,
    unit_price,
    CURRENT_DATE AS loaded_at
FROM raw_dim_product
WHERE product_id IS NOT NULL;
