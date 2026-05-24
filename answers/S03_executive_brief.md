# Brief exécutif — S03 : Vérité historique dans les dimensions NexaMart

> **Question du CEO (S03) :** quels changements dans nos dimensions doivent garder la vérité historique, et lesquels peuvent être écrasés ?
>
> **Contexte :** des clients changent de segment, des magasins changent de région, des noms sont corrigés. Le CEO veut des rapports fiables **par rapport à la réalité au moment de la vente**, pas celle d’aujourd’hui.

## Réponse exécutive

Avant S03, nos dimensions client utilisaient un modèle équivalent à un **écrasement (Type 1)** : chaque changement de segment remplaçait l’ancienne valeur. Les ventes passées étaient alors rattachées au segment **actuel**, ce qui faussait les tableaux de bord (ex. ventes « New » qui appartenaient en réalité au segment « Inactive »).

Nous avons adopté une **politique SCD** documentée dans [`docs/scd-policy.md`](../docs/scd-policy.md) : **Type 2** pour `segment`, `city` et `région` client ainsi que pour la **région magasin** ; **Type 1** pour les corrections de nom et le type de magasin. Le entrepôt conserve désormais plusieurs versions par client avec `valid_from`, `valid_to` et `is_current`, et les faits joignent la version valide à la date de commande.

**Impact mesurable :** sur notre jeu de données, le chiffre d’affaires attribué au segment Gold diffère de **129,78 $** entre le rapport trompeur et le rapport correct ; pour le client **CUS-00152**, **5 527,41 $** passent de « New » (faux) à « Inactive » (juste).

## Décisions de modélisation

| Élément | Décision |
|---------|----------|
| Attribut pilote | **`dim_customer.segment`** — utilisé dans les rapports marketing et exécutifs |
| Historisation | **SCD Type 2** avec clé substitut par version (`customer_key`) |
| Corrections de nom | **SCD Type 1** — pas de nouvelle ligne |
| Magasin | **`région` → Type 2** ; **`store_type` → Type 1** |
| Jointure fait | `order_date` entre `valid_from` et `valid_to` ([`sql/facts/fact_sales.sql`](../sql/facts/fact_sales.sql)) |

Politique complète : [`docs/scd-policy.md`](../docs/scd-policy.md).

## Preuve — rapport trompeur vs rapport correct

Fichier canonique : [`sql/scd/type1_vs_type2_demo.sql`](../sql/scd/type1_vs_type2_demo.sql).

### Agrégat par segment — Type 1 (trompeur)

```sql
-- Segment = dernière valeur connue (écrasement)
SELECT c.segment, ROUND(SUM(f.line_total), 2) AS total_revenue
FROM raw_fact_sales f
JOIN demo_dim_customer_type1 c ON f.customer_id = c.customer_id
GROUP BY 1 ORDER BY 2 DESC;
```

| segment | total_revenue ($) | line_count |
|---------|------------------:|-----------:|
| Silver | 167 208,70 | — |
| Bronze | 149 999,28 | — |
| Gold | 118 773,28 | — |
| New | 97 824,99 | — |
| Inactive | 81 398,39 | — |
| Platinum | 45 910,30 | — |

### Agrégat par segment — Type 2 (correct)

```sql
SELECT c.segment, ROUND(SUM(f.line_total), 2) AS total_revenue
FROM raw_fact_sales f
JOIN dim_customer c
  ON f.customer_id = c.customer_id
 AND CAST(f.order_date AS DATE) >= c.valid_from
 AND (c.valid_to IS NULL OR CAST(f.order_date AS DATE) < c.valid_to)
GROUP BY 1 ORDER BY 2 DESC;
```

| segment | total_revenue ($) | line_count |
|---------|------------------:|-----------:|
| Silver | 174 621,80 | — |
| Bronze | 153 603,30 | — |
| Gold | 118 643,50 | — |
| New | 93 743,22 | — |
| Inactive | 80 483,78 | — |
| Platinum | 40 019,34 | — |

### Exemple client CUS-00152 (même montant, mauvais segment)

| Approche | Segment affiché | Chiffre d’affaires ($) |
|----------|-----------------|----------------------:|
| Type 1 (trompeur) | New | 5 527,41 |
| Type 2 (correct) | Inactive | 5 527,41 |

Le montant est identique, mais le **segment est faux** sous Type 1 — typique d’une décision marketing mal informée si l’on cible le segment « New ».

## Validation

| Contrôle | Résultat |
|----------|----------|
| `scd2_one_current` — une version courante par `customer_id` | PASS |
| `dim_customer.customer_key` unique | PASS |
| `fact_sales` — 3 000 lignes, grain unique | PASS |
| Écart Gold Type 1 vs Type 2 | 129,78 $ ([`sql/scd/type1_vs_type2_demo.sql`](../sql/scd/type1_vs_type2_demo.sql)) |
| Requêtes exécutées sur `db/nexamart.duckdb` (seed `team_3577855103`) | Oui |

## Risques / limites

- **Type 3** (colonne `previous_segment`) non déployé en S03 — réservé aux cas « une seule transition suffit » (S08).
- **Produit** : reclassements catalogue toujours en Type 1 ; une refonte d’assortiment majeure exigerait une revue.
- **Complexité** : plus de lignes en `dim_customer` (443 vs 285) et jointures temporelles — coût assumé pour la fidélité des rapports.
- Les **corrections de nom** n’ouvrent pas de version ; si un changement de nom reflétait une fusion d’entités, il faudrait une règle métier distincte.

## Prochaine recommandation

1. **Geler** la politique SCD dans [`docs/scd-policy.md`](../docs/scd-policy.md) comme référence pour tout nouveau attribut dimensionnel.
2. **Industrialiser** les chargements de changements (`raw_customer_changes`, `raw_store_changes`) dans le pipeline hebdomadaire.
3. En **S04–S06**, étendre la même logique aux faits complémentaires (`fact_returns`) pour des drill-across cohérents.

**Références :** [`docs/scd-policy.md`](../docs/scd-policy.md), [`docs/board-briefs/s03-scd.md`](../docs/board-briefs/s03-scd.md), [`docs/visuals/scd-type2-before-after.md`](../docs/visuals/scd-type2-before-after.md).
