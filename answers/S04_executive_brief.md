# Brief exécutif — S04 : Profils de commande et affinités de panier

> **Question du CEO (S04) :** quels patterns de commande NexaMart sont importants pour les opérations, et quels produits sont achetés ensemble ?

## Réponse exécutive

Les commandes opérationnelles ne se lisent pas en huit colonnes booléennes. Sur notre seed, **99 profils distincts** existent réellement (sur **256** combinaisons théoriques). Les deux patterns dominants sont **Achat employé** (175 commandes, 23,2 %) et **Livraison fragile** (135, 17,9 %). Côté panier, les paires les plus fréquentes croisent souvent **Home & Garden** et **Books & Media** (9 paniers identiques chacune sur les cinq premières paires observées).

**Décision proposée au VP Opérations :** renforcer capacité picking/livraison pour les profils **fragile** et **employé** ; lancer un test merchandising **Home & Garden + Books & Media** en bundle, car la co-occurrence est stable sur nos ventes actuelles.

## Décisions de modélisation

| Élément | Décision |
|---------|----------|
| Numéro de commande | **Dimension dégénérée** `order_number` dans `fact_sales` — pas de `dim_order` (aucun attribut descriptif utile). |
| Drapeaux opérationnels | **Junk dimension** `dim_order_profile` — 8 flags consolidés, **profils nommés** (`profile_name`). |
| Lien au fait | `profile_key` (FK optionnelle) via `raw_orders` ; **aucune mesure** dans la junk dim. |
| Panier | Self-join `fact_sales` sur `order_number`, `product_key` ordonné pour éviter les doublons (A,B)/(B,A). |

**Justification junk vs flags séparés :** 2⁸ = **256** combinaisons théoriques ; nous n’en observons que **99** (~39 % du cube). Huit colonnes dans le fait obligeraient le VP à recomposer des masques binaires ; une junk dimension expose directement des libellés métier et réduit le bruit du schéma.

## Preuve

### Profils opérationnels agrégés

```sql
SELECT
    p.profile_name,
    COUNT(DISTINCT f.order_number) AS order_count,
    ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales AS f
INNER JOIN dim_order_profile AS p ON f.profile_key = p.profile_key
GROUP BY 1
ORDER BY 2 DESC
LIMIT 8;
```

| profile_name | order_count | total_revenue ($) |
|--------------|------------:|------------------:|
| Achat employé | 175 | 122 892,72 |
| Livraison fragile | 135 | 90 008,57 |
| Commande standard | 94 | 66 633,10 |
| Ramassage en ligne | 71 | 52 188,96 |
| Cadeau promotionnel | 61 | 41 679,38 |
| Ramassage promo | 52 | 37 679,24 |
| Profil mixte opérationnel | 51 | 40 706,25 |
| Emballage cadeau | 39 | 29 742,03 |

### Top 5 paires produits co-achetés

```sql
SELECT
    pa.name AS product_a,
    pb.name AS product_b,
    COUNT(*) AS times_bought_together
FROM fact_sales f1
JOIN fact_sales f2
    ON f1.order_number = f2.order_number AND f1.product_key < f2.product_key
JOIN dim_product pa ON f1.product_key = pa.product_key
JOIN dim_product pb ON f2.product_key = pb.product_key
GROUP BY 1, 2
ORDER BY 3 DESC
LIMIT 5;
```

| product_a | product_b | times_bought_together |
|-----------|-----------|----------------------:|
| Electronics Item 2 | Sports & Outdoors Item 9 | 9 |
| Home & Garden Item 9 | Books & Media Item 3 | 9 |
| Home & Garden Item 5 | Books & Media Item 10 | 9 |
| Home & Garden Item 3 | Beauty & Health Item 7 | 9 |
| Home & Garden Item 6 | Pet Supplies Item 5 | 9 |

## Validation

- Pipeline : `make generate` → `make load` → `make check` (Windows : `.\run.ps1`).
- Grain `fact_sales` : **3 000** lignes, clé composite `(order_number, sale_line_id)` unique (`grain_unique_fact_sales` PASS).
- `dim_order_profile` : **99** lignes, **sans mesures** ; table présente (`TABLE_EXISTS` PASS).
- Couverture `profile_key` : **755** commandes sur **934** distinctes dans `fact_sales` (~81 %) — les commandes hors fichier S04 `raw_orders` restent à `NULL` (limite documentée, pas une erreur de jointure).

## Risques / limites

- **Couverture partielle** : les drapeaux S04 ne couvrent pas toutes les commandes du fait ventes rechargé (S06) ; les profils ne s’appliquent qu’aux `order_number` présents dans `raw_orders`.
- **Panier = co-occurrence**, pas causalité : une paire fréquente ne prouve pas qu’un produit entraîne l’achat de l’autre.
- **Noms de profils** : les combinaisons rares sont regroupées sous « Profil mixte opérationnel » — à affiner si le VP exige une granularité fine.

## Prochaine recommandation

1. **Valider** un pilote opérationnel sur les profils **Achat employé** et **Livraison fragile** (SLA picking + emballage).
2. **Tester** un bundle merchandising **Home & Garden × Books & Media** sur 4 semaines avec suivi du taux d’attachement.
3. **Exit ticket CEO :** le conseil peut désormais **prioriser les investissements logistiques par profil nommé** et **lancer des offres panier ciblées** sur des paires produits mesurées — au lieu d’interpréter manuellement huit drapeaux par ligne.

## Reproduction

```bash
make generate
make load
make check
make sql FILE=sql/analysis/basket_pairs.sql
```

Références : [docs/schema-v2.md](../docs/schema-v2.md), [docs/profiles.md](../docs/profiles.md), [docs/board-briefs/s04-basket-flags.md](../docs/board-briefs/s04-basket-flags.md).
