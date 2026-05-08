-- ============================================================
-- checks.sql — Validation de l'entrepôt NexaMart
-- ============================================================
-- Exécuté par : make check  /  .\run.ps1 check (legacy, src/run_checks.py)
--           ET : src/run_session_checks.py (subset par session via @rule)
-- Produit : validation/results/check_results.txt
--
-- Convention : chaque check retourne check_type, detail, result (PASS/FAIL)
--
-- Annotations `-- @rule: <name>` : run_session_checks.py découpe ce fichier
-- par marqueurs `@rule:` et n'exécute que les blocs dont le nom apparaît
-- dans `warehouse_checks` du session_manifest.yaml. Ces commentaires sont
-- ignorés par src/run_checks.py qui exécute toujours tout (legacy).
-- ============================================================

-- @rule: tables_exist
-- ─────────────────────────────────────────────
-- 1. Existence des tables clés
-- ─────────────────────────────────────────────
-- Bug fix (mai 2026) : l'ancienne version retournait 0 ligne quand
-- AUCUNE table n'existait, ce qui silenciait totalement le check.
-- On enumère explicitement la liste attendue via VALUES + LEFT JOIN
-- pour qu'une table absente apparaisse en FAIL au lieu de disparaître.
WITH expected(table_name) AS (
    VALUES ('dim_date'), ('dim_product'), ('dim_store'),
           ('dim_customer'), ('dim_channel'),
           ('fact_sales'), ('fact_returns'), ('fact_budget'),
           ('fact_daily_inventory'), ('fact_order_pipeline'),
           ('bridge_customer_segment'), ('junk_order_profile'),
           ('fact_promo_exposure')
)
SELECT 'TABLE_EXISTS'              AS check_type,
       e.table_name                AS detail,
       CASE WHEN i.table_name IS NULL
            THEN 'FAIL -- table not present'
            ELSE 'PASS' END         AS result
FROM expected e
LEFT JOIN information_schema.tables i
       ON i.table_schema = 'main'
      AND i.table_name = e.table_name;

-- @rule: fact_sales_not_empty
-- ─────────────────────────────────────────────
-- 2. Tables non vides (cardinalité minimale)
-- ─────────────────────────────────────────────
SELECT 'ROW_COUNT' AS check_type,
       'dim_date'  AS detail,
       CASE WHEN COUNT(*) >= 365 THEN 'PASS' ELSE 'FAIL -- expected >=365 rows' END AS result
FROM dim_date;

SELECT 'ROW_COUNT' AS check_type,
       'dim_product' AS detail,
       CASE WHEN COUNT(*) >= 10 THEN 'PASS' ELSE 'FAIL -- expected >=10 rows' END AS result
FROM dim_product;

SELECT 'ROW_COUNT' AS check_type,
       'dim_store'  AS detail,
       CASE WHEN COUNT(*) = 10 THEN 'PASS' ELSE 'FAIL -- expected 10 rows' END AS result
FROM dim_store;

SELECT 'ROW_COUNT' AS check_type,
       'dim_channel' AS detail,
       CASE WHEN COUNT(*) = 5 THEN 'PASS' ELSE 'FAIL -- expected 5 rows' END AS result
FROM dim_channel;

SELECT 'ROW_COUNT' AS check_type,
       'dim_customer' AS detail,
       CASE WHEN COUNT(*) >= 100 THEN 'PASS' ELSE 'FAIL -- expected >=100 rows' END AS result
FROM dim_customer;

SELECT 'ROW_COUNT' AS check_type,
       'fact_sales' AS detail,
       CASE WHEN COUNT(*) >= 500 THEN 'PASS' ELSE 'FAIL -- expected >=500 rows' END AS result
FROM fact_sales;

-- @rule: dim_keys_unique
-- ─────────────────────────────────────────────
-- 3. Clés primaires uniques (dimensions)
-- ─────────────────────────────────────────────
SELECT 'PK_UNIQUE' AS check_type,
       'dim_date.date_key' AS detail,
       CASE WHEN COUNT(*) = COUNT(DISTINCT date_key) THEN 'PASS'
            ELSE 'FAIL — duplicate date_key' END AS result
FROM dim_date;

SELECT 'PK_UNIQUE' AS check_type,
       'dim_product.product_id' AS detail,
       CASE WHEN COUNT(*) = COUNT(DISTINCT product_id) THEN 'PASS'
            ELSE 'FAIL — duplicate product_id' END AS result
FROM dim_product;

SELECT 'PK_UNIQUE' AS check_type,
       'dim_store.store_id' AS detail,
       CASE WHEN COUNT(*) = COUNT(DISTINCT store_id) THEN 'PASS'
            ELSE 'FAIL — duplicate store_id' END AS result
FROM dim_store;

SELECT 'PK_UNIQUE' AS check_type,
       'dim_channel.channel_id' AS detail,
       CASE WHEN COUNT(*) = COUNT(DISTINCT channel_id) THEN 'PASS'
            ELSE 'FAIL — duplicate channel_id' END AS result
FROM dim_channel;

-- @rule: dim_customer_pk_unique
-- dim_customer : on vérifie la clé substitut (customer_key) car celle-ci
-- reste unique quel que soit le SCD choisi. Sous Type 2, le customer_id
-- natural peut apparaître plusieurs fois (une par version), donc on
-- vérifie plutôt qu'il n'y a jamais DEUX versions actives pour le même
-- customer_id au même moment (chevauchement de périodes).
SELECT 'PK_UNIQUE' AS check_type,
       'dim_customer.customer_key' AS detail,
       CASE WHEN COUNT(*) = COUNT(DISTINCT customer_key) THEN 'PASS'
            ELSE 'FAIL — duplicate customer_key' END AS result
FROM dim_customer;

-- @rule: scd2_one_current
-- Vérification SCD2 : au plus une version courante par customer_id.
-- Si dim_customer est en Type 1, is_current n'existe pas -- le check
-- est alors SKIP (table_exists catch dans run_checks.py).
SELECT 'SCD2_ONE_CURRENT' AS check_type,
       'dim_customer one is_current per customer_id' AS detail,
       CASE WHEN COUNT(*) FILTER (WHERE n_current > 1) = 0 THEN 'PASS'
            ELSE 'FAIL — multiple current versions for same customer_id' END AS result
FROM (
    SELECT customer_id, COUNT(*) AS n_current
    FROM dim_customer
    WHERE is_current = TRUE
    GROUP BY customer_id
) t;

-- @rule: fact_sales_no_null_fk
-- ─────────────────────────────────────────────
-- 4. FK NOT NULL dans fact_sales
-- ─────────────────────────────────────────────
-- Convention Kimball : les faits joignent les dimensions via la clé
-- substitut (*_key), pas la clé naturelle (*_id). Si votre fact_sales
-- utilise customer_id au lieu de customer_key, renommez la colonne --
-- ces checks sont la référence.
SELECT 'FK_NOT_NULL' AS check_type,
       'fact_sales.product_key' AS detail,
       CASE WHEN COUNT(*) FILTER (WHERE product_key IS NULL) = 0 THEN 'PASS'
            ELSE 'FAIL — NULL product_key found' END AS result
FROM fact_sales;

SELECT 'FK_NOT_NULL' AS check_type,
       'fact_sales.store_key' AS detail,
       CASE WHEN COUNT(*) FILTER (WHERE store_key IS NULL) = 0 THEN 'PASS'
            ELSE 'FAIL — NULL store_key found' END AS result
FROM fact_sales;

SELECT 'FK_NOT_NULL' AS check_type,
       'fact_sales.customer_key' AS detail,
       CASE WHEN COUNT(*) FILTER (WHERE customer_key IS NULL) = 0 THEN 'PASS'
            ELSE 'FAIL — NULL customer_key found' END AS result
FROM fact_sales;

SELECT 'FK_NOT_NULL' AS check_type,
       'fact_sales.channel_key' AS detail,
       CASE WHEN COUNT(*) FILTER (WHERE channel_key IS NULL) = 0 THEN 'PASS'
            ELSE 'FAIL — NULL channel_key found' END AS result
FROM fact_sales;

-- @rule: grain_unique_fact_sales
-- ─────────────────────────────────────────────
-- 5. Grain verification — fact_sales
--    (order_number + sale_line_id should be unique)
-- ─────────────────────────────────────────────
SELECT 'GRAIN_UNIQUE' AS check_type,
       'fact_sales (order_number, sale_line_id)' AS detail,
       CASE WHEN COUNT(*) = COUNT(DISTINCT (order_number || '-' || sale_line_id))
            THEN 'PASS' ELSE 'FAIL — grain violation' END AS result
FROM fact_sales;

-- @rule: reconcile_sales_vs_budget
-- ─────────────────────────────────────────────
-- 6. Drill-across réconciliation (S06)
--    Revenue in fact_sales vs budget target — sanity only
-- ─────────────────────────────────────────────
-- Tolérant au pré-S06 : run_checks.py attrape CatalogException et
-- marque le check SKIP tant que fact_budget n'est pas construite.
SELECT 'RECONCILE' AS check_type,
       'sales_total vs budget_total' AS detail,
       CASE WHEN ABS(s.total - b.total) / NULLIF(b.total, 0) < 2.0
            THEN 'PASS' ELSE 'FAIL -- large variance vs budget' END AS result
FROM (SELECT SUM(line_total) AS total FROM fact_sales) s,
     (SELECT SUM(target_revenue) AS total FROM fact_budget) b;

-- @rule: bridge_weights_sum_to_one
-- ─────────────────────────────────────────────
-- 7. Bridge weights sum to 1.0 per customer (S08)
-- ─────────────────────────────────────────────
-- Tolérant au pré-S08 : run_checks.py attrape CatalogException et
-- marque le check SKIP tant que bridge_customer_segment n'est pas
-- construite. Active automatiquement à S08.
-- Convention Kimball : on groupe par la surrogate key (customer_key)
-- et non la clé naturelle. La bridge_customer_segment du
-- reference-solution utilise customer_key -- la convention enforce-ée.
SELECT 'BRIDGE_WEIGHT' AS check_type,
       'bridge_customer_segment SUM(weight)=1.0' AS detail,
       CASE WHEN COUNT(*) FILTER (WHERE ABS(w - 1.0) > 0.01) = 0
            THEN 'PASS' ELSE 'FAIL -- weights do not sum to 1.0' END AS result
FROM (SELECT customer_key, SUM(weight) AS w
      FROM bridge_customer_segment GROUP BY customer_key) t;
