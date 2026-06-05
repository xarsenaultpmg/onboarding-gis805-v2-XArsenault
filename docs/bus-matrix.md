# Bus matrix — NexaMart S07

> **Question CEO (S07) :** le board peut-il voir ventes, retours, inventaire et budget dans une seule vue sans mentir ?

La réponse dépend de la conformité des dimensions. Une case `X` signifie que le processus utilise la même dimension via une FK et peut être agrégé à n'importe quel grain de cette dimension. Une case `~` signifie une **conformité partielle par rollup** : l'attribut partagé est un sous-ensemble agrégé de la dimension (ex. `category` sans `product_key`). Une case vide signifie que la dimension n'est pas applicable.

## Matrice processus × dimensions conformes

| Processus / table de faits | Grain | `dim_date` | `dim_product` | `dim_store` | `dim_customer` | `dim_channel` |
|---|---|---:|---:|---:|---:|---:|
| `fact_sales` | Ligne de commande (`sale_line_id`) | X | X | X | X | X |
| `fact_returns` | Ligne de retour (`return_id`) | X | X | X | X | X |
| `fact_inventory_snapshot` | Snapshot jour × produit × magasin | X | X | X |  |  |
| `fact_budget` | Mois × catégorie × magasin | X | ~ | X |  |  |

> **`~` pour `fact_budget × dim_product` :** `fact_budget` ne contient pas de `product_key`. La colonne `category` est un `VARCHAR` brut dont les valeurs doivent correspondre exactement à `dim_product.category`. Le drill-across avec `fact_sales` est valide **au grain catégorie uniquement** — on ne peut pas descendre au niveau produit individuel dans le budget.

## Décision de grain partagé

Pour le drill-across S07, les faits ne sont jamais joints directement. Chaque fait est d'abord agrégé au **grain commun** requis par la question :

- **Ventes × retours** : `category × mois`, via `dim_product` et `dim_date`.
- **Réel × budget** : `category × store_key × mois`, via `dim_product`, `dim_store` et `dim_date`.
- **Inventaire** : `category × store_key × mois` si on compare les niveaux de stock aux ventes ou au budget.

Cette décision évite le produit cartésien : `fact_sales` et `fact_returns` ont chacun plusieurs lignes par produit et par mois. Les joindre directement multiplierait les montants; les agréger séparément conserve les totaux.

## Règles de conformité

1. `dim_product.category` est le libellé de référence pour comparer ventes, retours, inventaire et budget.
2. `fact_budget.category` reste un `VARCHAR`, mais doit correspondre exactement aux valeurs de `dim_product.category`.
3. `dim_date` sert à ramener les dates transactionnelles (`date_key`) au mois via `DATE_TRUNC('month', d."date")`.
4. `dim_store` porte la vérité SCD2 du magasin; les faits utilisent `store_key` pour pointer la bonne version.
5. Les dimensions `dim_customer` et `dim_channel` sont conformes pour ventes et retours, mais non applicables à budget et inventaire.

## Contrôles S07

- Requête drill-across : [`sql/integration/s07-drill-across.sql`](../sql/integration/s07-drill-across.sql)
- Réel-vs-budget : [`sql/integration/s07-actual-vs-budget.sql`](../sql/integration/s07-actual-vs-budget.sql)
- Réconciliation : [`sql/checks/s07-reconciliation.sql`](../sql/checks/s07-reconciliation.sql)

Les contrôles attendus comparent les totaux directs des tables de faits aux totaux agrégés par CTE. Un écart de `0.00` est requis avant de publier un chiffre au board.
