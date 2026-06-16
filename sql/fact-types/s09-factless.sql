-- ============================================================
-- S09 — Factless Fact Table
-- ============================================================
-- GRAIN : une ligne = un client × une campagne × une date d'exposition
-- TYPE  : Factless Fact Table
-- RÈGLE : Pas de mesure numérique — la PRÉSENCE de la ligne est le fait.
--         La seule agrégation de base est COUNT(*).
--         La requête inverse (NOT EXISTS / NOT IN) est aussi importante
--         que la requête directe.
-- ============================================================
--
-- Run avec :
--   duckdb db/nexamart.duckdb -c ".read sql/fact-types/s09-factless.sql"
-- ============================================================

-- ── Étape 1 : Explorer la table ──────────────────────────────
-- Combien d'expositions ? Combien de clients uniques exposés ?

SELECT
    COUNT(*)                        AS total_expositions,
    COUNT(DISTINCT customer_key)    AS clients_uniques_exposes,
    COUNT(DISTINCT campaign_id)     AS nb_campagnes,
    COUNT(DISTINCT channel_key)     AS nb_canaux,
    MIN(exposure_date)              AS premiere_exposition,
    MAX(exposure_date)              AS derniere_exposition
FROM fact_promo_exposure;


-- ── Étape 2 : Couverture par campagne ───────────────────────
-- Calcule le nombre d'expositions et de clients uniques par campagne.
--        Quel canal a généré le plus d'expositions pour chaque campagne ?

SELECT
    campaign_id,
    COUNT(*)                            AS nb_expositions,
    COUNT(DISTINCT customer_key)        AS nb_clients_uniques,
    COUNT(DISTINCT channel_key)         AS nb_canaux,
    MIN(exposure_date)                  AS premiere_exposition,
    MAX(exposure_date)                  AS derniere_exposition
FROM fact_promo_exposure
GROUP BY 1
ORDER BY nb_expositions DESC;


-- ── Étape 3 : Répartition par canal ─────────────────────────
-- Calcule le % des expositions par canal.
--        Jointure : fact_promo_exposure → dim_channel

SELECT
    dc.channel_name,
    COUNT(*)                              AS nb_expositions,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_total
FROM fact_promo_exposure AS e
INNER JOIN dim_channel AS dc
    ON dc.channel_key = e.channel_key
GROUP BY 1
ORDER BY nb_expositions DESC;


-- ── Étape 4 : Requête inverse — clients NON exposés ──────────
-- Calcule combien de clients actifs n'ont PAS été exposés à une campagne.
--        Comparez ce nombre au total de clients actifs.
--        Jointure : dim_customer (is_current = TRUE)

SELECT
    COUNT(*) AS total_clients_actifs,
    COUNT(*) FILTER (WHERE e.customer_key IS NULL) AS clients_actifs_non_exposes,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE e.customer_key IS NULL) / COUNT(*),
        1
    ) AS pct_clients_non_exposes
FROM dim_customer AS c
LEFT JOIN (
    SELECT DISTINCT customer_key
    FROM fact_promo_exposure
) AS e
    ON e.customer_key = c.customer_key
WHERE c.is_current = TRUE;


-- ── Note sur la factless fact ─────────────────────────────────
-- Si vous ajoutez un montant (ex. coût d'impression par exposition),
-- ce n'est plus une factless fact — c'est une table transactionnelle
-- avec une mesure de coût.
-- La question diagnostic : "Y a-t-il un nombre qui caractérise chaque
-- ligne individuellement ?" → OUI = transactionnelle, NON = factless.
