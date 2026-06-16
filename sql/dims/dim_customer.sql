-- Dimension client SCD Type 2 (segment, ville, province) + Type 1 (correction de nom).
-- Source : raw_dim_customer + raw_customer_changes (S03).

CREATE OR REPLACE TABLE dim_customer AS
WITH base AS (
    SELECT
        customer_id,
        CAST(join_date AS DATE) AS event_date,
        loyalty_segment AS segment,
        city,
        province,
        first_name || ' ' || last_name AS name
    FROM raw_dim_customer
),
scd_events AS (
    SELECT
        customer_id,
        CAST(change_date AS DATE) AS event_date,
        CASE WHEN change_type = 'segment_change' THEN new_value END AS segment,
        CASE WHEN change_type = 'city_move' THEN new_value END AS city,
        CASE WHEN change_type = 'province_change' THEN new_value END AS province
    FROM raw_customer_changes
    WHERE change_type IN ('segment_change', 'city_move', 'province_change')
),
timeline AS (
    SELECT customer_id, event_date, segment, city, province, name FROM base
    UNION ALL
    SELECT customer_id, event_date, segment, city, province, NULL::VARCHAR AS name
    FROM scd_events
),
filled AS (
    SELECT
        customer_id,
        event_date,
        LAST_VALUE(segment IGNORE NULLS) OVER w AS segment,
        LAST_VALUE(city IGNORE NULLS) OVER w AS city,
        LAST_VALUE(province IGNORE NULLS) OVER w AS province,
        LAST_VALUE(name IGNORE NULLS) OVER w AS name
    FROM timeline
    WINDOW w AS (
        PARTITION BY customer_id
        ORDER BY event_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )
),
versions AS (
    SELECT
        customer_id,
        event_date AS valid_from,
        LEAD(event_date) OVER (
            PARTITION BY customer_id ORDER BY event_date
        ) AS valid_to,
        name,
        segment,
        city,
        province
    FROM (
        SELECT DISTINCT customer_id, event_date, segment, city, province, name
        FROM filled
    ) AS distinct_events
),
name_corrected AS (
    SELECT
        v.customer_id,
        v.valid_from,
        v.valid_to,
        COALESCE(
            (
                SELECT nc.new_value
                FROM raw_customer_changes AS nc
                WHERE nc.customer_id = v.customer_id
                  AND nc.change_type = 'name_correction'
                  AND CAST(nc.change_date AS DATE) >= v.valid_from
                  AND (
                      v.valid_to IS NULL
                      OR CAST(nc.change_date AS DATE) < v.valid_to
                  )
                ORDER BY nc.change_date DESC
                LIMIT 1
            ),
            v.name
        ) AS name,
        v.segment,
        v.city,
        v.province,
        (v.valid_to IS NULL) AS is_current
    FROM versions AS v
)
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id, valid_from)::BIGINT AS customer_key,
    customer_id,
    name,
    segment,
    city,
    province AS "région",
    valid_from,
    valid_to,
    is_current,
    CURRENT_DATE AS loaded_at
FROM name_corrected
WHERE customer_id IS NOT NULL;
