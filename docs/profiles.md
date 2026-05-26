# Profils de commande NexaMart (S04)

Trace processus : fréquences observées sur le seed d’équipe (`team_3577855103`) après `make generate` et `make load`.

## Synthèse

| Métrique | Valeur |
|----------|--------|
| Commandes avec drapeaux (`raw_orders`) | 755 |
| Combinaisons théoriques (8 drapeaux) | 256 |
| Combinaisons observées (`dim_order_profile`) | 99 |
| Taux d’exploration du cube de flags | 38,7 % (99/256) |

## Profils nommés par fréquence (niveau commande)

Requête source :

```sql
SELECT
    p.profile_name,
    COUNT(*) AS order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders
FROM raw_orders AS o
INNER JOIN dim_order_profile AS p
    ON  o.is_gift_wrapped = p.is_gift_wrapped
    AND o.is_express_shipping = p.is_express_shipping
    AND o.is_loyalty_redeemed = p.is_loyalty_redeemed
    AND o.is_promo_applied = p.is_promo_applied
    AND o.is_employee_purchase = p.is_employee_purchase
    AND o.is_online_pickup = p.is_online_pickup
    AND o.is_fragile = p.is_fragile
    AND o.is_oversized = p.is_oversized
GROUP BY 1
ORDER BY 2 DESC;
```

| profile_name | order_count | pct_of_orders | Flags actifs (résumé) |
|--------------|------------:|--------------:|------------------------|
| Achat employé | 175 | 23,2 % | `is_employee_purchase` |
| Livraison fragile | 135 | 17,9 % | `is_fragile` |
| Commande standard | 94 | 12,5 % | aucun drapeau |
| Ramassage en ligne | 71 | 9,4 % | `is_online_pickup` |
| Cadeau promotionnel | 61 | 8,1 % | `is_gift_wrapped` + `is_promo_applied` |
| Ramassage promo | 52 | 6,9 % | `is_online_pickup` + `is_promo_applied` |
| Profil mixte opérationnel | 51 | 6,8 % | combinaisons rares non nommées individuellement |
| Emballage cadeau | 39 | 5,2 % | `is_gift_wrapped` |
| Hors gabarit | 20 | 2,6 % | `is_oversized` |
| Livraison express | 20 | 2,6 % | `is_express_shipping` |
| Promo fidélité | 18 | 2,4 % | `is_promo_applied` + `is_loyalty_redeemed` |
| Express fragile | 12 | 1,6 % | `is_express_shipping` + `is_fragile` |
| Cadeau express | 4 | 0,5 % | cadeau + express |
| Express fidélité | 3 | 0,4 % | express + fidélité |

## Corrélation promo × fidélité (exemple VP)

Sur les 755 commandes S04 : **19** combinent promo et fidélité ; **226** ont une promo seule. Utile pour valider que la junk dimension regroupe bien des **patterns** plutôt que des colonnes isolées.

## Reproduction

```bash
make generate
make load
```

Windows : `.\run.ps1 generate` puis `.\run.ps1 load`.
