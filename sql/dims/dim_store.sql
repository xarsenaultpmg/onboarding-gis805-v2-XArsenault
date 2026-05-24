-- Dimension magasin : région = SCD Type 2 ; store_type = SCD Type 1 (écrasement).
-- Source : raw_dim_store + raw_store_changes (S03).

CREATE OR REPLACE TABLE dim_store AS
WITH base AS (
    SELECT
        store_id,
        CAST('2024-01-01' AS DATE) AS event_date,
        region,
        store_type
    FROM raw_dim_store
),
region_events AS (
    SELECT
        store_id,
        CAST(change_date AS DATE) AS event_date,
        new_value AS region
    FROM raw_store_changes
    WHERE change_type = 'region_reassign'
),
timeline AS (
    SELECT store_id, event_date, region, store_type FROM base
    UNION ALL
    SELECT store_id, event_date, region, NULL::VARCHAR AS store_type
    FROM region_events
),
filled AS (
    SELECT
        store_id,
        event_date,
        LAST_VALUE(region IGNORE NULLS) OVER w AS region,
        LAST_VALUE(store_type IGNORE NULLS) OVER w AS store_type
    FROM timeline
    WINDOW w AS (
        PARTITION BY store_id
        ORDER BY event_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )
),
versions AS (
    SELECT
        store_id,
        event_date AS valid_from,
        LEAD(event_date) OVER (
            PARTITION BY store_id ORDER BY event_date
        ) AS valid_to,
        region,
        store_type
    FROM (
        SELECT DISTINCT store_id, event_date, region, store_type
        FROM filled
    ) AS distinct_events
),
current_type AS (
    SELECT
        store_id,
        new_value AS store_type
    FROM raw_store_changes
    WHERE change_type = 'type_upgrade'
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY store_id ORDER BY change_date DESC
    ) = 1
)
SELECT
    ROW_NUMBER() OVER (ORDER BY s.store_id, v.valid_from)::BIGINT AS store_key,
    s.store_id,
    s.store_name AS name,
    s.city,
    v.region AS "région",
    s.province,
    COALESCE(ct.store_type, v.store_type) AS store_type,
    v.valid_from,
    v.valid_to,
    (v.valid_to IS NULL) AS is_current,
    CURRENT_DATE AS loaded_at
FROM versions AS v
INNER JOIN raw_dim_store AS s
    ON v.store_id = s.store_id
LEFT JOIN current_type AS ct
    ON v.store_id = ct.store_id
WHERE s.store_id IS NOT NULL;
