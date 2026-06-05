# Brief exécutif — S07 : Vue entreprise intégrée NexaMart

> **Question du CEO (S07) :** le board peut-il voir ventes, retours, inventaire et budget dans une seule vue sans mentir ?

## Réponse exécutive

Oui, à condition de ne jamais joindre les tables de faits directement. Le modèle S07 intègre **4 faits** (`fact_sales`, `fact_returns`, `fact_inventory_snapshot`, `fact_budget`) via des dimensions conformes documentées dans [`docs/bus-matrix.md`](../docs/bus-matrix.md).

Le drill-across ventes × retours utilise le grain commun **catégorie × mois** via `dim_product` et `dim_date`. Sur notre seed, **Automotive en mars 2025** affiche le taux de remboursement le plus élevé : **931,92 $** de remboursements sur **4 351,32 $** de ventes, soit **21,42 %**. Côté réel-vs-budget, la plus forte sous-performance observée est **Sports & Outdoors — NexaMart Calgary — mai 2025** : **741,33 $** de ventes réelles contre **101 657,54 $** de budget, soit **-100 916,21 $ (-99,3 %)**.

## Décisions de modélisation

| Élément | Décision |
|---------|----------|
| Bus matrix | Documentée dans [`docs/bus-matrix.md`](../docs/bus-matrix.md), avec 4 faits × 5 dimensions. |
| Drill-across ventes-retours | Agrégation séparée de `fact_sales` et `fact_returns`, puis `FULL OUTER JOIN` au grain `category × mois`. |
| Réel-vs-budget | Agrégation de `fact_sales` au grain de `fact_budget` : `category × store_key × mois`. |
| Budget | `category` reste un libellé métier, pas une FK; la conformité vient de la correspondance avec `dim_product.category`. |
| Inventaire | `fact_inventory_snapshot` partage `dim_date`, `dim_product`, `dim_store`; les niveaux de stock ne sont pas sommés sur le temps sans précaution. |

**Règle de gouvernance :** chaque KPI multi-faits doit nommer son grain commun et les dimensions conformes utilisées. Sinon, le rapport peut être faux même si le SQL s'exécute.

## Preuve — drill-across ventes × retours

Fichier : [`sql/integration/s07-drill-across.sql`](../sql/integration/s07-drill-across.sql)

```sql
WITH sales_agg AS (...),
     returns_agg AS (...)
SELECT ...
FROM sales_agg AS s
FULL OUTER JOIN returns_agg AS r
  ON s.category = r.category
 AND s.mois = r.mois;
```

| Catégorie | Mois | Ventes ($) | Remboursements ($) | Net ($) | Taux remboursement |
|---|---:|---:|---:|---:|---:|
| Automotive | 2025-03 | 4 351,32 | 931,92 | 3 419,40 | 21,42 % |
| Beauty & Health | 2025-12 | 1 938,23 | 401,86 | 1 536,37 | 20,73 % |
| Toys & Games | 2025-12 | 11 942,29 | 1 887,91 | 10 054,38 | 15,81 % |
| Beauty & Health | 2025-09 | 2 597,54 | 325,83 | 2 271,71 | 12,54 % |
| Books & Media | 2025-10 | 12 533,03 | 1 515,49 | 11 017,54 | 12,09 % |

**Lecture business :** Automotive en mars n'est pas le plus gros volume, mais son taux de remboursement est le signal qualité le plus fort. C'est une cible prioritaire pour analyser les causes de retour (`return_reason`) avant la prochaine revue des fournisseurs.

## Preuve — réel vs budget

Fichier : [`sql/integration/s07-actual-vs-budget.sql`](../sql/integration/s07-actual-vs-budget.sql)

| Catégorie | Magasin | Mois | Réel ($) | Budget ($) | Écart ($) | Écart % |
|---|---|---:|---:|---:|---:|---:|
| Sports & Outdoors | NexaMart Calgary | 2025-05 | 741,33 | 101 657,54 | -100 916,21 | -99,3 % |
| Grocery | NexaMart Vancouver | 2025-02 | 289,50 | 100 764,20 | -100 474,70 | -99,7 % |
| Automotive | NexaMart Rive-Sud | 2025-06 | 0,00 | 98 251,36 | -98 251,36 | -100,0 % |
| Pet Supplies | NexaMart Sherbrooke | 2025-07 | 510,94 | 98 294,80 | -97 783,86 | -99,5 % |
| Beauty & Health | NexaMart Calgary | 2025-02 | 0,00 | 97 524,35 | -97 524,35 | -100,0 % |

**Lecture business :** les cibles budgétaires sont fortement supérieures aux ventes observées sur plusieurs combinaisons catégorie × magasin × mois. Le CFO peut maintenant distinguer une sous-performance commerciale d'un budget potentiellement mal calibré, car les deux mesures sont comparées au même grain.

## Signal inventaire

`fact_inventory_snapshot` complète la vue entreprise sans être joint directement aux ventes. Au grain catégorie × province, les snapshots sous le point de réapprovisionnement les plus fréquents sont :

| Catégorie | Province | Snapshots sous seuil | Stock moyen | Point de réappro moyen |
|---|---|---:|---:|---:|
| Sports & Outdoors | QC | 41 | 12,5 | 23,4 |
| Home & Garden | QC | 37 | 13,7 | 24,6 |
| Grocery | QC | 30 | 12,4 | 24,3 |
| Automotive | QC | 30 | 12,0 | 21,3 |
| Home & Garden | ON | 29 | 14,7 | 22,9 |

Ce signal sert à prioriser les enquêtes : une catégorie peut manquer son budget parce que la demande est faible, mais aussi parce que le stock disponible est insuffisant.

## Validation

Fichier : [`sql/checks/s07-reconciliation.sql`](../sql/checks/s07-reconciliation.sql)

| Contrôle | Total direct | Total agrégé | Résultat |
|---|---:|---:|---|
| `fact_sales` vs `sales_agg` | 661 114,94 | 661 114,94 | PASS |
| `fact_returns` vs `returns_agg` | 27 008,72 | 27 008,72 | PASS |
| `fact_sales` vs `actual` | 661 114,94 | 661 114,94 | PASS |
| `fact_budget` vs `budget` | 54 207 450,79 | 54 207 450,79 | PASS |

Les analyses S07 utilisent les tables modélisées (`fact_*`, `dim_*`). Les tables `raw_*` ne servent qu'à construire les faits dans le pipeline.

## Risques / limites

- Le budget est fourni au grain catégorie × magasin × mois; il ne permet pas d'expliquer les écarts par client ou canal.
- Les chiffres de budget semblent très élevés par rapport aux ventes observées; il faut vérifier si la cible représente un scénario annuel, un objectif agressif ou un problème de calibrage.
- L'inventaire est semi-additif : on peut l'agréger par produit ou magasin, mais pas sommer naïvement plusieurs dates pour parler d'un stock total dans le temps.
- Le drill-across ne remplace pas une attribution causale. Un retour élevé peut venir d'un défaut fournisseur, d'un canal, d'un transporteur ou d'un changement de mix produit.

## Prochaine recommandation

1. Investiguer **Automotive mars 2025** pour comprendre le taux de remboursement de **21,42 %**.
2. Revoir avec le CFO les catégories-magasins où le budget dépasse le réel de plus de **95 %**.
3. Croiser les sous-performances avec les snapshots sous seuil de stock, sans joindre directement les faits : toujours agréger au grain commun avant comparaison.

**Références :** [`docs/bus-matrix.md`](../docs/bus-matrix.md), [`docs/board-briefs/s07-enterprise-view.md`](../docs/board-briefs/s07-enterprise-view.md), [`docs/visuals/drill-across-pattern.md`](../docs/visuals/drill-across-pattern.md).
