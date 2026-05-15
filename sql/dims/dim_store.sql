-- Dimension magasin (diapo NexaMart) : store_key, name, city, région, province.
-- Source : raw_dim_store. « région » = region du fichier source.

CREATE OR REPLACE TABLE dim_store AS
SELECT
    ROW_NUMBER() OVER (ORDER BY store_id)::BIGINT AS store_key,
    store_id,
    store_name AS name,
    city,
    region AS "région",
    province,
    store_type,
    CURRENT_DATE AS loaded_at
FROM raw_dim_store
WHERE store_id IS NOT NULL;
