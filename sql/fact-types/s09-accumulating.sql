-- ============================================================
-- S09 — Snapshot accumulant (Accumulating Snapshot)
-- ============================================================
-- GRAIN : une ligne = une commande complète avec ses jalons
-- TYPE  : Accumulating Snapshot Fact Table
-- RÈGLE : C'est le SEUL type de table de faits qu'on UPDATE.
--         Les dates de jalons non atteints sont NULL — ce n'est
--         pas une erreur, c'est une commande encore en cours.
-- JALONS : order_date → payment_date → pick_date → ship_date → delivery_date
-- ============================================================
--
-- Run avec :
--   duckdb db/nexamart.duckdb -c ".read sql/fact-types/s09-accumulating.sql"
-- ============================================================

-- ── Étape 1 : Explorer la table ──────────────────────────────
-- Combien de commandes ? Comment se répartissent-elles par statut ?

SELECT
    current_status,
    COUNT(*)                                    AS nb_commandes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_total
FROM fact_order_pipeline
GROUP BY 1
ORDER BY nb_commandes DESC;


-- ── Étape 2 : Funnel de complétion par jalon ─────────────────
-- TODO : Quel % des commandes a atteint chaque jalon ?
--        Utilisez les colonnes booléennes reached_payment, reached_pick,
--        reached_ship, reached_delivery.
--        Attendu : pct_payment ≥ pct_pick ≥ pct_ship ≥ pct_delivery

-- [Votre requête ici]
-- Squelette :
-- SELECT
--     COUNT(*) AS total_commandes,
--     ROUND(100.0 * SUM(reached_payment::INT)  / COUNT(*), 1) AS pct_payment,
--     ROUND(100.0 * SUM(reached_pick::INT)     / COUNT(*), 1) AS pct_pick,
--     ROUND(100.0 * SUM(reached_ship::INT)     / COUNT(*), 1) AS pct_ship,
--     ROUND(100.0 * SUM(reached_delivery::INT) / COUNT(*), 1) AS pct_delivery
-- FROM fact_order_pipeline;


-- ── Étape 3 : Délais moyens entre jalons ─────────────────────
-- TODO : Calculez le délai moyen (en jours) entre chaque étape,
--        pour les commandes qui ont atteint TOUS les jalons.
--        Utilisez delivery_date - order_date pour le délai total.
--        Filtrez avec WHERE delivery_date IS NOT NULL.

-- [Votre requête ici]


-- ── Étape 4 : Requête CEO ─────────────────────────────────────
-- TODO : Répondez à la question "Quel % des commandes est livré et
--        quel est le délai moyen de livraison ?"
--        Format attendu : une ligne par statut avec délai moyen et %

-- [Votre requête ici]


-- ── Note sur les NULL ─────────────────────────────────────────
-- Les NULL dans delivery_date et ship_date représentent des commandes
-- en cours, pas des données manquantes. Ne les filtrez pas dans le
-- funnel — ils font partie de l'information (commandes non livrées).
-- Dans votre brief : expliquez au CEO pourquoi pct_delivery < 100%.
