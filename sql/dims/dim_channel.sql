-- Dimension canal : source raw_dim_channel après chargement CSV dans DuckDB.
-- Clé substitut : channel_key (ROW_NUMBER). Clé naturelle : channel_id.
-- Supprime une ancienne table dim_promo si elle traînait dans la base (cohérence Sprint 1 vs ancienne variante « promo »).

DROP TABLE IF EXISTS dim_promo;

CREATE OR REPLACE TABLE dim_channel AS
SELECT
    ROW_NUMBER() OVER (ORDER BY channel_id)::BIGINT AS channel_key,
    channel_id,
    channel_name,
    channel_type,
    CURRENT_DATE AS loaded_at
FROM raw_dim_channel
WHERE channel_id IS NOT NULL;
