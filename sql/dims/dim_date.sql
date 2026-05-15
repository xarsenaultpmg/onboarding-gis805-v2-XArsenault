-- Dimension date (diapo NexaMart) : date_key, date, month, quarter, year.
-- date_key = substitut (ROW_NUMBER). Colonne date = jour calendaire (jointure chargement).

CREATE OR REPLACE TABLE dim_date AS
SELECT
    ROW_NUMBER() OVER (ORDER BY src.date_key)::BIGINT AS date_key,
    src.date_key AS "date",
    src.year,
    src.quarter,
    src.month,
    src.month_name,
    src.week_iso,
    src.day_of_week,
    src.day_name,
    src.is_weekend,
    CURRENT_DATE AS loaded_at
FROM raw_dim_date AS src
WHERE src.date_key IS NOT NULL;
