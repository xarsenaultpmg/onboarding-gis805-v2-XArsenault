-- S02 — Ventes par catégorie, région et trimestre (question CEO S01).
-- Fait : fact_sales (revenue = revenue diapo). Dimensions : dim_product, dim_store, dim_date.
--
-- Exécution (CLI DuckDB, si installé) : duckdb db/nexamart.duckdb -c ".read sql/analysis/s02-first-answer.sql"
-- Exécution (sans CLI — recommandé Windows) : python scripts/run_sql.py sql/analysis/s02-first-answer.sql
--   ou : .\run.ps1 sql sql\analysis\s02-first-answer.sql   |   .\run.ps1 sql -SqlFile sql\analysis\s02-first-answer.sql
--   Unix : make sql FILE=sql/analysis/s02-first-answer.sql

SELECT
    p.category,
    s."région" AS region,
    d.quarter,
    SUM(f.revenue) AS total_sales,
    COUNT(*)       AS line_count
FROM fact_sales AS f
INNER JOIN dim_product AS p
    ON f.product_key = p.product_key
INNER JOIN dim_store AS s
    ON f.store_key = s.store_key
INNER JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY
    p.category,
    s."région",
    d.quarter
ORDER BY
    total_sales DESC;
