# Bus Matrix — NexaMart S10

Cette matrice montre quelles dimensions sont conformes entre les processus
NexaMart. Une case `X` signifie que la table de faits porte une FK vers la
dimension. Une case `~` indique une conformité partielle par rollup ou par
pont. Une case vide signifie que la dimension n'est pas applicable au grain du
processus.

## Matrice processus x dimensions conformes

| Processus / table de faits | Grain | Type | `dim_date` | `dim_product` | `dim_store` | `dim_customer` | `dim_channel` | `dim_order_profile` | `dim_segment_outrigger` |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Ventes / `fact_sales` | Ligne de commande (`sale_line_id` + `order_number`) | Transaction | X | X | X | X | X | X | ~ |
| Retours / `fact_returns` | Ligne de retour (`return_id`) | Transaction | X | X | X | X | X |  | ~ |
| Inventaire S07 / `fact_inventory_snapshot` | Snapshot produit x magasin x date | Periodic snapshot | X | X | X |  |  |  |  |
| Budget / `fact_budget` | Mois x catégorie x magasin | Periodic snapshot budgétaire | X | ~ | X |  |  |  |  |
| Transactions S09 / `fact_orders_transaction` | Transaction atomique (`transaction_id`) | Transaction | X | X | X | X |  |  | ~ |
| Inventaire quotidien S09 / `fact_daily_inventory` | Produit x magasin x jour | Periodic snapshot | X | X | X |  |  |  |  |
| Pipeline commandes / `fact_order_pipeline` | Commande suivie dans son cycle (`order_id`) | Accumulating snapshot | X | X | X | X |  |  | ~ |
| Expositions promo / `fact_promo_exposure` | Client x campagne x date d'exposition | Factless | X |  |  | X | X |  | ~ |

## Notes de conformité

- `fact_budget` ne contient pas de `product_key`. Sa colonne `category`
  correspond à `dim_product.category`, donc les comparaisons avec ventes,
  retours ou inventaire sont valides au grain catégorie seulement.
- `dim_segment_outrigger` est accessible par `bridge_customer_segment`, pas
  directement depuis les faits. La case `~` signale qu'il faut passer par
  `customer_key` puis appliquer les poids du pont.
- `fact_order_pipeline` utilise `order_date_key` comme date conforme principale.
  Les jalons `payment_date`, `pick_date`, `ship_date` et `delivery_date` restent
  dans la table pour les délais, mais ne sont pas encore des role-playing FK.
- `fact_promo_exposure.campaign_id` est une dimension dégénérée. Il n'existe
  pas de `dim_campaign` dans le modèle courant.

## Grains communs recommandés

| Question | Faits comparés | Grain commun sûr |
|---|---|---|
| Revenu vs remboursements | `fact_sales`, `fact_returns` | Catégorie x mois, ou produit x mois si la question ne touche pas le budget |
| Réel vs budget | `fact_sales`, `fact_budget` | Catégorie x magasin x mois |
| Stock vs ventes | `fact_daily_inventory`, `fact_sales` | Produit ou catégorie x magasin x jour/mois, avec moyenne de stock sur le temps |
| Funnel livraison | `fact_order_pipeline` seul | Commande, statut courant ou mois de commande |
| Couverture promotionnelle | `fact_promo_exposure`, `dim_customer` | Client courant x canal x période |
| Revenu par segment pondéré | `fact_sales`, `bridge_customer_segment`, `dim_segment_outrigger` | Segment x période, avec `SUM(revenue * weight)` |

## Règles de drill-across

1. Ne jamais joindre deux tables de faits au niveau ligne. Chaque fait est
   d'abord agrégé au grain commun de la question, puis les agrégats sont joints.
2. Utiliser `dim_date` pour ramener les dates transactionnelles au mois avec
   `DATE_TRUNC('month', d."date")` quand la question est mensuelle.
3. Utiliser `dim_product.category` comme libellé de référence pour tout rapport
   qui inclut `fact_budget`.
4. Utiliser les clés substitutives SCD2 (`customer_key`, `store_key`) déjà
   résolues dans les faits pour préserver la vérité historique.
5. Pour les segments M:N, publier seulement des montants pondérés ou expliciter
   qu'un rapport est une attribution primaire non réconciliable au total réel.
6. Pour les snapshots d'inventaire, utiliser des moyennes ou des derniers jours
   de période sur l'axe temps ; ne pas sommer le stock sur plusieurs jours.

## Contrôles et preuves

- Requête drill-across : [`sql/integration/s07-drill-across.sql`](../sql/integration/s07-drill-across.sql)
- Réel-vs-budget : [`sql/integration/s07-actual-vs-budget.sql`](../sql/integration/s07-actual-vs-budget.sql)
- Réconciliation S07 : [`sql/checks/s07-reconciliation.sql`](../sql/checks/s07-reconciliation.sql)
- Allocation pondérée S08 : [`sql/bridges/s08-weighted-allocation.sql`](../sql/bridges/s08-weighted-allocation.sql)
- Réconciliation du pont : [`sql/checks/s08-weighted-reconciliation.sql`](../sql/checks/s08-weighted-reconciliation.sql)
- Analyses S09 : [`sql/fact-types/`](../sql/fact-types/)

Un chiffre destiné au board doit toujours pouvoir être relié à une requête de
réconciliation ou à une règle de grain documentée ci-dessus.
