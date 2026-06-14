-- ============================================================
-- S09 — Snapshot périodique
-- ============================================================
-- GRAIN : une ligne = un produit × un magasin × un jour
-- TYPE  : Periodic Snapshot Fact Table
-- RÈGLE : Les mesures sont SEMI-ADDITIVES.
--         quantity_on_hand est additif sur produits et magasins,
--         mais PAS sur le temps — ne jamais SUM sur des périodes !
--         Utilisez AVG() ou LAST_VALUE() sur la dimension temps.
-- ============================================================
--
-- Run avec :
--   duckdb db/nexamart.duckdb -c ".read sql/fact-types/s09-periodic-snapshot.sql"
-- ============================================================

-- ── Étape 1 : Vérifier le grain ──────────────────────────────
-- Le grain est respecté si total_lignes = lignes_grain_unique.
-- product_key × store_key × snapshot_date doit être la clé naturelle.

SELECT
    COUNT(*)                                                    AS total_lignes,
    COUNT(DISTINCT (product_key, store_key, snapshot_date))     AS lignes_grain_unique
FROM fact_daily_inventory;
-- Attendu : les deux colonnes sont égales.


-- ── Étape 2a : ❌ FAUX — SUM sur le temps (à exécuter pour observer) ─
-- ATTENTION : Cette requête produit un chiffre absurde.
-- Elle additionne des photos différentes du même stock à des dates
-- différentes — comme additionner votre solde bancaire de lundi + mardi.
-- Exécutez-la, notez le résultat, puis comparez avec l'étape 2b.

SELECT
    p.category,
    SUM(i.quantity_on_hand)   AS stock_cumule_FAUX
FROM fact_daily_inventory i
JOIN dim_product p ON p.product_key = i.product_key
GROUP BY 1
ORDER BY stock_cumule_FAUX DESC;


-- ── Étape 2b : ✓ CORRECT — AVG sur le temps ─────────────────
-- Calcule le stock moyen par catégorie de produit.
--        Ajoutez aussi le stock max, min et le nombre de jours d'observation.
--        Notez dans votre brief le ratio stock_cumule_FAUX / stock_moyen ≈ nb_jours.

SELECT
    p.category,
    ROUND(AVG(i.quantity_on_hand), 1)     AS stock_moyen,
    MAX(i.quantity_on_hand)               AS stock_max,
    MIN(i.quantity_on_hand)               AS stock_min,
    COUNT(DISTINCT i.snapshot_date)       AS nb_jours_observation
FROM fact_daily_inventory AS i
INNER JOIN dim_product AS p
    ON p.product_key = i.product_key
GROUP BY 1
ORDER BY stock_moyen DESC;


-- ── Étape 3 : Requête CEO — Stock moyen sur les 5 derniers jours ─
-- Calcule le stock moyen et les jours d'approvisionnement moyens
--        pour chaque magasin, sur les 5 dernières dates de snapshot disponibles.
--        Utiliser un CTE pour isoler les 5 dernières dates.

WITH derniers_jours AS (
    SELECT DISTINCT snapshot_date
    FROM fact_daily_inventory
    ORDER BY snapshot_date DESC
    LIMIT 5
)
SELECT
    ds.name                               AS store_name,
    ds."région"                          AS region,
    ROUND(AVG(i.quantity_on_hand), 1)     AS stock_moyen_5j,
    ROUND(AVG(i.days_of_supply), 1)       AS jours_approvisionnement_moyen
FROM fact_daily_inventory AS i
INNER JOIN derniers_jours AS d
    ON d.snapshot_date = i.snapshot_date
INNER JOIN dim_store AS ds
    ON ds.store_key = i.store_key
GROUP BY 1, 2
ORDER BY stock_moyen_5j DESC;
