-- Junk dimension S04 : combinaisons distinctes des 8 drapeaux opérationnels (raw_orders).
-- Pas de mesures — uniquement descriptifs + profile_name pour le VP Opérations.

CREATE OR REPLACE TABLE dim_order_profile AS
WITH distinct_flags AS (
    SELECT DISTINCT
        is_gift_wrapped,
        is_express_shipping,
        is_loyalty_redeemed,
        is_promo_applied,
        is_employee_purchase,
        is_online_pickup,
        is_fragile,
        is_oversized
    FROM raw_orders
),
named AS (
    SELECT
        is_gift_wrapped,
        is_express_shipping,
        is_loyalty_redeemed,
        is_promo_applied,
        is_employee_purchase,
        is_online_pickup,
        is_fragile,
        is_oversized,
        CASE
            WHEN is_gift_wrapped = 0 AND is_express_shipping = 0 AND is_loyalty_redeemed = 0
                 AND is_promo_applied = 0 AND is_employee_purchase = 0 AND is_online_pickup = 0
                 AND is_fragile = 0 AND is_oversized = 0
                THEN 'Commande standard'
            WHEN is_express_shipping = 1 AND is_loyalty_redeemed = 1 AND is_gift_wrapped = 0
                THEN 'Express fidélité'
            WHEN is_promo_applied = 1 AND is_loyalty_redeemed = 1
                THEN 'Promo fidélité'
            WHEN is_gift_wrapped = 1 AND is_promo_applied = 1
                THEN 'Cadeau promotionnel'
            WHEN is_express_shipping = 1 AND is_fragile = 1
                THEN 'Express fragile'
            WHEN is_online_pickup = 1 AND is_promo_applied = 1
                THEN 'Ramassage promo'
            WHEN is_employee_purchase = 1
                THEN 'Achat employé'
            WHEN is_oversized = 1 AND is_fragile = 0
                THEN 'Hors gabarit'
            WHEN is_fragile = 1 AND is_oversized = 0
                THEN 'Livraison fragile'
            WHEN is_gift_wrapped = 1 AND is_express_shipping = 1
                THEN 'Cadeau express'
            WHEN is_online_pickup = 1 AND is_express_shipping = 0
                THEN 'Ramassage en ligne'
            WHEN is_express_shipping = 1
                THEN 'Livraison express'
            WHEN is_gift_wrapped = 1
                THEN 'Emballage cadeau'
            ELSE 'Profil mixte opérationnel'
        END AS profile_name
    FROM distinct_flags
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY profile_name, is_gift_wrapped, is_express_shipping, is_loyalty_redeemed,
                 is_promo_applied, is_employee_purchase, is_online_pickup, is_fragile, is_oversized
    )::BIGINT AS profile_key,
    is_gift_wrapped,
    is_express_shipping,
    is_loyalty_redeemed,
    is_promo_applied,
    is_employee_purchase,
    is_online_pickup,
    is_fragile,
    is_oversized,
    profile_name
FROM named;
