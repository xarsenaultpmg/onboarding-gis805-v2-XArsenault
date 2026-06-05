-- ============================================================
-- GRAIN : une ligne = un mois x une catégorie x un magasin.
-- Modèle S07 : budget mensuel comparable aux ventes agrégées au même grain.
--   - category reste un libellé métier (VARCHAR), pas une FK vers dim_product
--   - Dimensions conformes : date_key (mois), store_key
-- Mesures : target_revenue, target_quantity
-- ============================================================

CREATE OR REPLACE TABLE fact_budget AS
SELECT
    d.date_key,
    s.store_key,
    b.budget_id,
    CAST(b.budget_month AS DATE) AS budget_month,
    b.category,
    b.target_revenue,
    b.target_units AS target_quantity
FROM raw_fact_budget AS b
INNER JOIN dim_date AS d
    ON CAST(b.budget_month AS DATE) = d."date"
INNER JOIN dim_store AS s
    ON b.store_id = s.store_id
   AND CAST(b.budget_month AS DATE) >= s.valid_from
   AND (s.valid_to IS NULL OR CAST(b.budget_month AS DATE) < s.valid_to);
