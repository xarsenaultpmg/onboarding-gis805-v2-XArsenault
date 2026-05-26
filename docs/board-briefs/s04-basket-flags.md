# Brief conseil — Profils de commande et panier (S04)

## Question du CEO (S04)

Quels patterns de commande NexaMart sont importants pour les opérations, et quels produits sont achetés ensemble ?

## Réponse en une page

NexaMart consolide **8 drapeaux opérationnels** dans une junk dimension **`dim_order_profile`** (99 combinaisons observées sur 256 théoriques). Le VP Opérations lit des **profils nommés** (« Achat employé », « Promo fidélité », « Commande standard ») au lieu de huit colonnes booléennes dans `fact_sales`.

**`order_number`** reste une **dimension dégénérée** dans le fait pour regrouper les lignes d’un panier. L’analyse d’affinité par **self-join** sur `fact_sales` montre des paires récurrentes (ex. *Home & Garden* + *Books & Media*, 9 co-occurrences sur notre seed).

**Recommandation VP :** prioriser la préparation **fragile** et le flux **achat employé** (≈ 41 % des commandes S04) ; tester des bundles **Home & Garden × Books & Media** en merchandising cross-canal.

## Pourquoi junk dimension (et pas 8 colonnes dans le fait)

| Approche | Inconvénient |
|----------|--------------|
| 8 colonnes dans `fact_sales` | Bruit, requêtes lourdes, noms non exécutifs |
| 8 mini-dimensions `dim_flag_*` | Modèle ingérable |
| **Junk `dim_order_profile`** | 1 FK, profils nommés, uniquement combinaisons **réellement observées** |

## Preuves techniques

- Modèle : [docs/schema-v2.md](../schema-v2.md), [sql/dims/dim_order_profile.sql](../../sql/dims/dim_order_profile.sql)
- Fréquences : [docs/profiles.md](../profiles.md)
- Panier : [sql/analysis/basket_pairs.sql](../../sql/analysis/basket_pairs.sql)
- Brief détaillé : [answers/S04_executive_brief.md](../../answers/S04_executive_brief.md)

## Reproduction

```bash
make generate && make load && make check
make sql FILE=sql/analysis/basket_pairs.sql
```
