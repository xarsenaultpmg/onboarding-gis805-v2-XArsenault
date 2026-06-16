-- ============================================================
-- GRAIN : une ligne = un client x une campagne x une date d'exposition.
-- Type S09 : Factless Fact Table.
--   - Dimensions conformes : date_key, customer_key, channel_key
--   - Dimension dégénérée : campaign_id
-- Mesures : aucune. La présence de la ligne est le fait.
-- ============================================================

CREATE OR REPLACE TABLE fact_promo_exposure AS
SELECT
    d.date_key,
    c.customer_key,
    ch.channel_key,
    e.exposure_id,
    CAST(e.exposure_date AS DATE) AS exposure_date,
    e.campaign_id
FROM raw_fact_promo_exposure AS e
INNER JOIN dim_date AS d
    ON CAST(e.exposure_date AS DATE) = d."date"
INNER JOIN dim_customer AS c
    ON e.customer_id = c.customer_id
   AND CAST(e.exposure_date AS DATE) >= c.valid_from
   AND (c.valid_to IS NULL OR CAST(e.exposure_date AS DATE) < c.valid_to)
INNER JOIN dim_channel AS ch
    ON e.channel_id = ch.channel_id;
