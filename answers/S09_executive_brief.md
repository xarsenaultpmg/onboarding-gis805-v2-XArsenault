# S09 Executive Brief — Les quatre types de tables de faits

## Question du CEO

Quels processus NexaMart sont transactionnels, quels sont des snapshots, et quels sont de simples présences ?

## Réponse exécutive

Oui, le board peut maintenant lire NexaMart avec les quatre types de faits Kimball, chacun aligné sur une question différente. Les transactions expliquent les événements de revenu : `fact_orders_transaction` contient **1 662 transactions** et **531 486,99 $** de revenu brut. Le stock quotidien est un snapshot périodique : le niveau de stock ne doit pas être additionné sur le temps. Le pipeline de commandes est un snapshot accumulant : **70,2 %** des commandes sont livrées, avec **10,3 jours** de délai moyen. L'exposition promotionnelle est factless : **132 expositions** existent, mais **59,6 %** des clients actifs n'ont pas été atteints.

## Décisions de modélisation

| Processus | Table | Type | Justification |
|---|---|---|---|
| Ventes | `fact_sales` | Transaction | Une ligne de commande est un événement passé, insert-only, avec montants additifs. |
| Ordres détaillés | `fact_orders_transaction` | Transaction | Une ligne = `transaction_id`; la table mélange ventes, retours et échanges au grain événementiel. |
| Retours | `fact_returns` | Transaction | Une ligne = un retour; `refund_amount` et `return_quantity` peuvent être sommés. |
| Stock quotidien | `fact_daily_inventory` | Periodic Snapshot | Une ligne = produit x magasin x jour; `quantity_on_hand` est semi-additif. |
| Pipeline commandes | `fact_order_pipeline` | Accumulating Snapshot | Une ligne = une commande, enrichie quand paiement, préparation, expédition et livraison progressent. |
| Exposition promo | `fact_promo_exposure` | Factless | Aucune mesure numérique; la présence de la ligne prouve l'exposition. |

## Preuve

Les requêtes de preuve sont dans :

| Type | Fichier | Chiffre réel observé |
|---|---|---:|
| Transaction | `sql/fact-types/s09-transaction.sql` | 1 662 transactions distinctes, 3 types, 531 486,99 $ de revenu brut |
| Periodic Snapshot | `sql/fact-types/s09-periodic-snapshot.sql` | 1 500 snapshots quotidiens au grain produit x magasin x jour |
| Accumulating Snapshot | `sql/fact-types/s09-accumulating.sql` | 301 commandes livrées sur 429, soit 70,2 %, délai moyen 10,3 jours |
| Factless | `sql/fact-types/s09-factless.sql` | 132 expositions promo; 170 clients actifs non exposés sur 285 |

## Le piège de la semi-additivité

Pour `Pet Supplies`, additionner le stock quotidien donne **18 682 unités**, alors que le stock moyen journalier est **622,7 unités**. Le ratio `SUM / AVG` est **30,0**, exactement le nombre de jours observés. Ce ratio prouve que `SUM(quantity_on_hand)` sur le temps recompte la même capacité de stock jour après jour.

## Validation

J'ai exécuté `.\run.ps1 generate`, `.\run.ps1 load`, puis `.\run.ps1 check` sur le seed `team_3577855103`. Le résultat final est **31 PASS, 0 FAIL, 0 SKIP**. Les grains clés sont vérifiés : `fact_orders_transaction` a **1 662 lignes** et **1 662 transaction_id distincts**; `fact_daily_inventory` respecte le grain produit x magasin x date; le pipeline conserve les commandes non livrées dans le funnel au lieu de les traiter comme des données manquantes.

## Risques / limites

`fact_orders_transaction.amount` ne doit pas être réconcilié directement avec `fact_sales.line_total` : ce sont deux grains différents, et la table S09 inclut aussi retours et échanges. Deux snapshots d'inventaire coexistent dans le dépôt (`fact_inventory_snapshot` pour S07 et `fact_daily_inventory` pour S09); les analyses S09 utilisent `fact_daily_inventory`. Enfin, `fact_promo_exposure` garde `campaign_id` comme dimension dégénérée, car aucune `dim_campaign` matérialisée n'existe dans le repo courant.

## Prochaine recommandation

Le CEO peut maintenant prioriser un suivi opérationnel des commandes non livrées : **29,8 %** du pipeline n'a pas encore atteint la livraison. Le prochain tableau de bord devrait suivre les commandes bloquées par statut (`pending_ship`, `pending_pick`, `pending_payment`, `cancelled`) et déclencher des alertes au-delà du délai moyen de **10,3 jours**.
