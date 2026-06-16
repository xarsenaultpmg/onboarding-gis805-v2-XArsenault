# Model Card — entrepôt NexaMart

Cette model card documente l'entrepôt analytique NexaMart tel qu'il existe
après S09. Elle sert à un analyste junior qui doit comprendre le modèle,
ses grains, ses limites et ses règles de validation sans relire tout le SQL.

## 1. Identification

- **Nom du modèle :** NexaMart Data Warehouse (GIS805)
- **Propriétaire :** Xavier Arsenault, Head of Data (simulation GIS805)
- **Dernière mise à jour :** 2026-06-15 (S10)
- **Version :** 0.10, brouillon handoff pack avant S11

## 2. Intention

### 2.1 Questions business couvertes

- Quel revenu, coût et volume NexaMart génère-t-il par produit, magasin,
  client, canal et période ?
- Quels produits, régions ou périodes concentrent les retours et les
  remboursements ?
- Le board peut-il comparer ventes, retours, inventaire et budget sans
  multiplier les montants par une mauvaise jointure entre faits ?
- Quels segments clients reçoivent le revenu quand un client appartient à
  plusieurs segments, et quelle est la différence entre attribution naïve et
  attribution pondérée ?
- Quels processus NexaMart relèvent d'une table transactionnelle, d'un
  snapshot périodique, d'un snapshot accumulatif ou d'une table factless ?

### 2.2 Questions hors scope

- Le modèle ne prédit pas la demande future ; il décrit les faits générés
  par le seed local.
- Il ne supporte pas encore le ciblage nominatif ou les données personnelles
  identifiables, car les clients sont synthétiques et les courriels sont
  réduits au domaine.
- Il ne modélise pas les paiements, split payments, taxes ou frais de
  livraison comme processus de faits séparés.

## 3. Structure

### 3.1 Tables de faits

| Fact | Grain | Type | Mesures principales | Dimensions reliées |
|---|---|---|---|---|
| `fact_sales` | Une ligne de commande (`sale_line_id` + `order_number`) | Transaction | `revenue`, `line_total`, `quantity`, `discount_amount`, `cost` | `dim_date`, `dim_product`, `dim_store`, `dim_customer`, `dim_channel`, `dim_order_profile` |
| `fact_returns` | Une ligne de retour (`return_id`) | Transaction | `refund_amount`, `return_quantity` | `dim_date`, `dim_product`, `dim_store`, `dim_customer`, `dim_channel` |
| `fact_inventory_snapshot` | Produit x magasin x date de snapshot | Periodic snapshot | `quantity_on_hand`, `quantity_on_order`, `reorder_point` | `dim_date`, `dim_product`, `dim_store` |
| `fact_budget` | Mois x catégorie x magasin | Periodic snapshot budgétaire | `target_revenue`, `target_quantity` | `dim_date`, `dim_store`, catégorie conforme par libellé |
| `fact_orders_transaction` | Une transaction atomique (`transaction_id`) | Transaction | `quantity`, `amount` | `dim_date`, `dim_product`, `dim_store`, `dim_customer` |
| `fact_daily_inventory` | Produit x magasin x jour | Periodic snapshot | `quantity_on_hand`, `quantity_on_order`, `days_of_supply` | `dim_date`, `dim_product`, `dim_store` |
| `fact_order_pipeline` | Une commande suivie dans son cycle de vie (`order_id`) | Accumulating snapshot | jalons, `days_order_to_deliver`, flags de jalons atteints | `dim_date` comme date de commande, `dim_product`, `dim_store`, `dim_customer` |
| `fact_promo_exposure` | Client x campagne x date d'exposition | Factless | aucune mesure ; la présence de la ligne est le fait | `dim_date`, `dim_customer`, `dim_channel` |

### 3.2 Dimensions

| Dimension | Type SCD | Clés | Notes |
|---|---|---|---|
| `dim_date` | Type 1 | `date_key`, `date` | Calendrier conforme pour jours, mois, trimestres et semaines ISO. |
| `dim_customer` | Type 2 + Type 1 | `customer_key`, `customer_id` | Segment, ville et province sont historisés ; corrections de nom sont écrasées. |
| `dim_store` | Type 2 + Type 1 | `store_key`, `store_id` | Région historisée ; type de magasin écrasé quand il s'agit d'une classification courante. |
| `dim_product` | Type 1 | `product_key`, `product_id` | Produit, catégorie, sous-catégorie, marque, coût et prix de référence. |
| `dim_channel` | Type 1 | `channel_key`, `channel_id` | Canal de vente et type de canal. |
| `dim_order_profile` | Junk dimension | `profile_key` | Regroupe huit drapeaux opérationnels de commande en profils nommés. |
| `dim_segment_outrigger` | Type 1 | `segment_key`, `segment` | Attributs de segment utilisés par le pont pondéré. |
| `dim_customer_scd3` | Type 3 | `customer_key`, `customer_id` | Segment actuel et segment précédent pour analyser les transitions récentes. |

### 3.3 Ponts et cas particuliers

- `bridge_customer_segment` modélise l'appartenance M:N entre clients et
  segments. La règle de conservation est `SUM(weight) = 1.0` par client.
- `fact_budget.category` n'a pas de `product_key` ; la conformité avec
  `dim_product` est donc valide seulement au grain catégorie.
- `order_number`, `transaction_id`, `order_id`, `campaign_id` et
  `original_sale_line_id` sont des dimensions dégénérées conservées dans les
  faits quand aucune dimension descriptive séparée n'est utile.
- Les dates de `fact_order_pipeline` sont des jalons dans une même ligne :
  `order_date`, `payment_date`, `pick_date`, `ship_date`, `delivery_date`.

## 4. Hypothèses clés et décisions structurantes

- Le grain de `fact_sales` reste la ligne de commande, pas l'en-tête de
  commande, pour préserver l'analyse par produit et catégorie.
- Les faits ne sont jamais joints directement entre eux pour un drill-across ;
  ils sont d'abord agrégés au grain commun de la question.
- `dim_customer` et `dim_store` utilisent le SCD Type 2 seulement pour les
  attributs qui changent l'interprétation historique d'un rapport.
- Les combinaisons de drapeaux opérationnels vivent dans `dim_order_profile`
  pour éviter huit colonnes répétées dans les rapports.
- Les segments clients M:N utilisent un pont pondéré pour éviter de créer du
  revenu fictif.
- Les quatre faits S09 sont séparés par type de processus, car additionner un
  snapshot quotidien ou traiter une exposition comme un montant donnerait des
  conclusions trompeuses.

Le détail de ces choix est dans `docs/decision-log.md`.

## 5. Qualité et fiabilité

### 5.1 Checks actifs

| Check | Ce qu'il protège | Référence |
|---|---|---|
| `TABLE_EXISTS` | Présence des tables attendues dans DuckDB | `validation/checks.sql` |
| `ROW_COUNT` | Cardinalités minimales des dimensions et faits clés | `validation/checks.sql` |
| `PK_UNIQUE` | Unicité des clés dimensionnelles | `validation/checks.sql` |
| `SCD2_ONE_CURRENT` | Au plus une version courante par client | `validation/checks.sql` |
| `FK_NOT_NULL` | Résolution des FK de `fact_sales` | `validation/checks.sql` |
| `GRAIN_UNIQUE` | Unicité du grain `fact_sales` | `validation/checks.sql` |
| `BRIDGE_WEIGHT` | Somme des poids de segment = 1.0 | `sql/checks/s08-weighted-reconciliation.sql` |

Les résultats courants sont produits par `.\run.ps1 check` dans
`validation/results/`.

### 5.2 Limites connues

- `dim_customer` contient une colonne `"région"` qui représente la province
  du client ; les rapports exécutifs doivent nommer clairement cet axe.
- `bridge_customer_segment` joint toutes les versions SCD2 d'un client pour
  couvrir l'historique ; les analyses temporelles fines doivent filtrer la
  version client appropriée.
- `fact_daily_inventory` et `fact_inventory_snapshot` sont semi-additifs :
  sommer le stock sur plusieurs jours gonfle artificiellement le niveau de
  stock.
- `fact_promo_exposure` ne prouve pas une conversion ou un achat ; elle prouve
  seulement l'exposition à une campagne.

## 6. Audience et usages acceptables

### 6.1 Pour qui

- Board NexaMart et CEO : décisions hebdomadaires sur ventes, retours,
  inventaire, budget, segments et promotions.
- Head of Data : validation de grains, SCD, ponts et règles de drill-across.
- Analyste junior : requêtes ad hoc au-dessus des dimensions conformes.

### 6.2 Pour quoi, pas

- Utiliser le warehouse pour des rapports agrégés, des comparaisons de
  performance et des preuves de modélisation.
- Ne pas l'utiliser pour des décisions client nominatives, de la prévision ou
  des analyses temps réel.
- Ne pas joindre deux tables de faits ligne à ligne ; toujours agréger chaque
  fait au grain commun avant de comparer.

## 7. Reproductibilité

- **Seed :** déterministe depuis le username GitHub.
- **Pipeline Windows :** `.\run.ps1 generate`, `.\run.ps1 load`,
  `.\run.ps1 check`.
- **Pipeline Unix :** `make generate && make load && make check`.
- **Version du code :** le commit courant est l'état canonique du modèle.

## 8. Historique

| Date | Version | Changement majeur | Référence |
|---|---|---|---|
| 2026-05-10 | 0.01 | Exploration initiale et premier brief CEO | `answers/S01_executive_brief.md` |
| 2026-05-14 | 0.02 | Première étoile `fact_sales` avec dimensions conformes | `docs/schema-v1.md` |
| 2026-05-21 | 0.03 | Politique SCD client et magasin | `docs/scd-policy.md` |
| 2026-05-25 | 0.04 | Dimension dégénérée et junk dimension de commande | `docs/profiles.md` |
| 2026-06-04 | 0.07 | Intégration entreprise ventes, retours, inventaire et budget | `docs/bus-matrix.md` |
| 2026-06-08 | 0.08 | Ponts pondérés et SCD Type 3 | `docs/board-briefs/s08-overlap-risk.md` |
| 2026-06-14 | 0.09 | Quatre types de tables de faits | `docs/fact-type-decision-tree.md` |
| 2026-06-15 | 0.10 | Handoff pack S10 en préparation | `docs/defense-template.md` |

---

*Cette model card est un livrable vivant. À chaque séance, elle doit permettre
à un remplaçant de comprendre le modèle et ses risques sans relire le SQL.*
