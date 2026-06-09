-- ============================================================
-- S09 — Table de faits transactionnelle
-- ============================================================
-- GRAIN : une ligne = une ligne de commande (order_id + sale_line_id)
-- TYPE  : Transaction Fact Table
-- RÈGLE : INSERT-ONLY — on n'update jamais une transaction passée.
--         Additif sur TOUTES les dimensions (SUM est toujours correct).
-- ============================================================
--
-- Run avec :
--   duckdb db/nexamart.duckdb -c ".read sql/fact-types/s09-transaction.sql"
-- ============================================================

-- ── Étape 1 : Vérifier le grain ──────────────────────────────
-- Exécutez cette requête AVANT d'écrire les vôtres.
-- Le grain est respecté si total_lignes > nb_commandes_distinctes
-- (plusieurs produits par commande).

SELECT
    COUNT(*)                    AS total_lignes,
    COUNT(DISTINCT order_id)    AS nb_commandes_distinctes
FROM fact_orders_transaction;


-- ── Étape 2 : Requête CEO 1 — Revenue par catégorie ─────────
-- TODO : Calculez le revenue brut, le coût total et la marge brute
--        par catégorie de produit.
--        Jointure requise : fact_orders_transaction → dim_product
--        Mesures : SUM(line_total), SUM(cost), SUM(line_total - cost)

-- [Votre requête ici]


-- ── Étape 3 : Requête CEO 2 — Top 5 magasins par marge ──────
-- TODO : Identifiez les 5 magasins avec la marge brute la plus élevée.
--        Jointure requise : fact_orders_transaction → dim_store
--        Résultat attendu : 5 lignes avec store_name, region, marge_brute

-- [Votre requête ici]


-- ── Étape 4 : Vérification de réconciliation ─────────────────
-- Le total de fact_orders_transaction doit correspondre à
-- la somme des requêtes CEO agrégées.

SELECT
    'total_direct'    AS methode,
    SUM(line_total)   AS revenue_total
FROM fact_orders_transaction
UNION ALL
SELECT
    'total_par_categorie',
    SUM(revenue_brut)
FROM (
    SELECT SUM(line_total) AS revenue_brut
    FROM fact_orders_transaction
    JOIN dim_product p ON p.product_key = fact_orders_transaction.product_key
    GROUP BY p.category
);
-- Attendu : les deux lignes affichent le même montant.
