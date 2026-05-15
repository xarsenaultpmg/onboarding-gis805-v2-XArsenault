-- Dimension client (diapo NexaMart) : customer_key, name, segment, city, région.
-- Source : raw_dim_customer. « région » mappée sur province (pas de région métier dans le CSV partagé).

CREATE OR REPLACE TABLE dim_customer AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id)::BIGINT AS customer_key,
    customer_id,
    first_name || ' ' || last_name AS name,
    loyalty_segment AS segment,
    city,
    province AS "région",
    first_name,
    last_name,
    email_domain,
    CAST(join_date AS DATE) AS join_date,
    CURRENT_DATE AS loaded_at
FROM raw_dim_customer
WHERE customer_id IS NOT NULL;
